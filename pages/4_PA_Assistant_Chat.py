import streamlit as st
import pandas as pd
from openai import OpenAI
import os
from PyPDF2 import PdfReader

import sys, os, pathlib
_here = pathlib.Path(__file__).resolve().parent
for _p in [_here.parent, _here, pathlib.Path(os.getcwd())]:
    if (_p / "theme.py").exists():
        if str(_p) not in sys.path: sys.path.insert(0, str(_p))
        break
try:
    from theme import apply_theme, SIDEBAR_HTML
except ImportError:
    def apply_theme(): pass
    SIDEBAR_HTML = "<p style=\'color:white\'>AIT</p>"

st.set_page_config(page_title="PA Assistant Chat", page_icon="💬", layout="wide")
apply_theme()

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)

st.title("💬 PA Assistant Chat")
st.markdown("ถาม-ตอบผู้ช่วยอัจฉริยะ (ตอบแบบมืออาชีพอ้างอิงคู่มือการปฏิบัติงานและผลการตรวจสอบที่ผ่านมา)")

# ── Helpers ───────────────────────────────────────────
def rewrite_query(user_question, chat_history, client):
    try:
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history[-2:]])
        system_prompt_rewrite = f"คุณคือ AI Query Rewriter\nหน้าที่: อ่านประวัติการคุย แล้วเขียนคำถามล่าสุดใหม่ให้สมบูรณ์ชัดเจน (ภาษาไทย)\nบริบท: {history_text}\nคำถามปัจจุบัน: {user_question}\nคำถามใหม่:"
        response = client.chat.completions.create(model="meta-llama/llama-3.3-70b-instruct:free", messages=[{"role":"user","content":system_prompt_rewrite}], temperature=0.3, max_tokens=150)
        return response.choices[0].message.content.strip()
    except Exception:
        return user_question

def filter_relevant_content(full_text, query, max_chars=100000):
    if not full_text: return ""
    if len(full_text) < max_chars: return full_text
    chunk_size = 2000
    chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
    query_words = set(query.replace("?","").split())
    scored_chunks = []
    for i, chunk in enumerate(chunks):
        score = sum(chunk.count(w) for w in query_words)
        if i < 3: score += 1
        scored_chunks.append((score, chunk))
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    final_context = ""
    current_chars = 0
    for score, chunk in scored_chunks:
        if current_chars + len(chunk) < max_chars:
            final_context += f"\n...[เนื้อหาที่เกี่ยวข้อง]...\n{chunk}"
            current_chars += len(chunk)
        else: break
    return final_context

def extract_text_from_files(files, folder_path="Doc"):
    text = ""
    if os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if filename.endswith('.pdf'):
                    with open(file_path,'rb') as f:
                        reader = PdfReader(f)
                        for page in reader.pages: text += page.extract_text() or ""
                elif filename.endswith('.txt'):
                    with open(file_path,'r',encoding='utf-8',errors='ignore') as f: text += f.read()
                elif filename.endswith('.csv'):
                    df = pd.read_csv(file_path); text += df.to_string()
            except Exception as e: print(f"Error reading {filename}: {e}")
    if files:
        for file in files:
            try:
                if file.name.endswith('.pdf'):
                    reader = PdfReader(file)
                    for page in reader.pages: text += page.extract_text() or ""
                elif file.name.endswith('.txt'): text += file.getvalue().decode("utf-8")
                elif file.name.endswith('.csv'):
                    df = pd.read_csv(file); text += df.to_string()
            except: pass
    return text

# ── Session Init ──────────────────────────────────────
def init_chat_state():
    ss = st.session_state
    ss.setdefault('chatbot_messages', [{"role":"assistant","content":"สวัสดีครับ PA Assistant พร้อมให้บริการครับ"}])
    ss.setdefault('file_context', "")
    ss.setdefault('last_processed_files', set())

init_chat_state()

# ── UI ────────────────────────────────────────────────
with st.expander("อัปโหลดเอกสารเพิ่มเติม (PDF, TXT, CSV)"):
    uploaded_files = st.file_uploader("เลือกไฟล์...", type=['pdf','txt','csv'], accept_multiple_files=True)

current_files_set = {f.name for f in uploaded_files} if uploaded_files else set()
is_files_changed  = current_files_set != st.session_state.last_processed_files
is_first_load     = not st.session_state.file_context and (uploaded_files or os.path.isdir("Doc"))

if is_files_changed or (is_first_load and not st.session_state.file_context):
    with st.spinner("กำลังประมวลผลเอกสาร..."):
        raw_text = extract_text_from_files(uploaded_files)
        if raw_text:
            st.session_state.file_context = raw_text
            st.session_state.last_processed_files = current_files_set
            st.success(f"✅ อ่านข้อมูลเรียบร้อย! ({len(raw_text):,} ตัวอักษร)")
        else:
            st.warning("ยังไม่มีข้อมูลเอกสาร")

chat_container = st.container(height=450, border=True)
with chat_container:
    for message in st.session_state.chatbot_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์คำถามของคุณ...", key="chat_input_main"):
    st.session_state.chatbot_messages.append({"role":"user","content":prompt})
    with chat_container:
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                # ── API keys ──────────────────────────────────────
                try:    typhoon_key    = st.secrets["api_key"]
                except: typhoon_key    = ""
                try:    openrouter_key = st.secrets["openrouter_api_key"]
                except: openrouter_key = ""

                # ── Rewrite query (ใช้ Typhoon ถ้ามี key) ─────────
                has_history  = len(st.session_state.chatbot_messages) > 1
                search_query = prompt
                if has_history and typhoon_key:
                    try:
                        rw_client = OpenAI(api_key=typhoon_key, base_url="https://api.opentyphoon.ai/v1")
                        rw_resp   = rw_client.chat.completions.create(
                            model="typhoon-v2.5-30b-a3b-instruct",
                            messages=[{"role":"user","content":
                                f"เขียนคำถามนี้ใหม่ให้สมบูรณ์ชัดเจน โดยอ้างอิงบริบท: "
                                f"{st.session_state.chatbot_messages[-2]['content'][:200]}\n"
                                f"คำถาม: {prompt}\nคำถามใหม่:"}],
                            temperature=0.3, max_tokens=150
                        )
                        search_query = rw_resp.choices[0].message.content.strip()
                    except Exception:
                        search_query = prompt

                # ── Build context ─────────────────────────────────
                final_context = filter_relevant_content(
                    st.session_state.file_context, search_query, max_chars=80000)
                if not final_context:
                    final_context = "ไม่พบข้อมูลในเอกสาร ตอบตามความรู้ทั่วไป"

                system_prompt = (
                    "คุณคือ PA Assistant ผู้เชี่ยวชาญการตรวจสอบผลสัมฤทธิ์ภาครัฐ\n"
                    "ตอบคำถามโดยอ้างอิงเนื้อหาด้านล่าง ถ้าไม่พบให้บอกว่า 'ไม่พบข้อมูลในเอกสารที่เกี่ยวข้อง'\n"
                    f"คำถาม: {prompt}\n"
                    "--- เนื้อหา ---\n" + final_context[:80000] + "\n---------------"
                )
                messages_for_api = [
                    {"role":"system","content":system_prompt},
                    {"role":"user",  "content":prompt}
                ]

                # ── Try providers in order ────────────────────────
                # 1st: Typhoon (paid, reliable)
                # 2nd-4th: OpenRouter free models (fallback)
                providers = []
                if typhoon_key:
                    providers.append(("typhoon", typhoon_key,
                                      "https://api.opentyphoon.ai/v1",
                                      "typhoon-v2.5-30b-a3b-instruct", {}))
                if openrouter_key:
                    hdrs = {"HTTP-Referer":"https://streamlit.io/","X-Title":"PA Chat"}
                    providers += [
                        ("qwen-free",     openrouter_key, "https://openrouter.ai/api/v1",
                         "qwen/qwen3-8b:free", hdrs),
                        ("llama-free",    openrouter_key, "https://openrouter.ai/api/v1",
                         "meta-llama/llama-3.1-8b-instruct:free", hdrs),
                        ("gemma-free",    openrouter_key, "https://openrouter.ai/api/v1",
                         "google/gemma-3-12b-it:free", hdrs),
                    ]

                if not providers:
                    message_placeholder.error("ไม่พบ API Key — กรุณาตั้งค่า `api_key` ใน Streamlit Secrets")
                    st.stop()

                stream = None
                used_provider = ""
                last_err = None
                for name, key, base_url, model, extra_hdrs in providers:
                    try:
                        c = OpenAI(api_key=key, base_url=base_url)
                        kwargs = dict(model=model, messages=messages_for_api, stream=True, max_tokens=2048)
                        if extra_hdrs:
                            kwargs["extra_headers"] = extra_hdrs
                        stream = c.chat.completions.create(**kwargs)
                        used_provider = name
                        break
                    except Exception as e:
                        last_err = e
                        continue

                if stream is None:
                    message_placeholder.error(f"ทุก provider ตอบไม่ได้: {last_err}")
                    st.stop()

                full_response = ""
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response += delta
                        message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)
                st.session_state.chatbot_messages.append(
                    {"role":"assistant","content":full_response})

            except Exception as e:
                st.error(f"Error: {e}")

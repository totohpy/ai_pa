import streamlit as st
import pandas as pd
from openai import OpenAI
import os, time
from PyPDF2 import PdfReader

import sys, pathlib
_here = pathlib.Path(__file__).resolve().parent
for _p in [_here.parent, _here, pathlib.Path(os.getcwd())]:
    if (_p / "theme.py").exists():
        if str(_p) not in sys.path: sys.path.insert(0, str(_p))
        break
try:
    from theme import apply_theme, SIDEBAR_HTML
except ImportError:
    def apply_theme(): pass
    SIDEBAR_HTML = ""

st.set_page_config(page_title="PA Assistant Chat", page_icon="💬", layout="wide")
apply_theme()

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)

st.title("💬 PA Assistant Chat")
st.markdown("ถาม-ตอบผู้ช่วยอัจฉริยะ อ้างอิงคู่มือการปฏิบัติงานและผลการตรวจสอบที่ผ่านมา")

# ── Helpers ───────────────────────────────────────────
def filter_relevant_content(full_text, query, max_chars=16000):
    if not full_text: return ""
    if len(full_text) <= max_chars: return full_text
    chunk_size = 1500
    chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
    query_words = set(query.replace("?","").split())
    scored = []
    for i, chunk in enumerate(chunks):
        score = sum(chunk.count(w) for w in query_words)
        if i < 3: score += 1
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    out, chars = "", 0
    for _, chunk in scored:
        if chars + len(chunk) > max_chars: break
        out += f"\n---\n{chunk}"
        chars += len(chunk)
    return out

def extract_text_from_files(files, folder_path="Doc"):
    text = ""
    if os.path.isdir(folder_path):
        for fn in os.listdir(folder_path):
            fp = os.path.join(folder_path, fn)
            try:
                if fn.endswith('.pdf'):
                    with open(fp,'rb') as f:
                        for pg in PdfReader(f).pages: text += pg.extract_text() or ""
                elif fn.endswith('.txt'):
                    with open(fp,'r',encoding='utf-8',errors='ignore') as f: text += f.read()
                elif fn.endswith('.csv'):
                    text += pd.read_csv(fp).to_string()
            except Exception as e: print(f"Error {fn}: {e}")
    if files:
        for file in files:
            try:
                if file.name.endswith('.pdf'):
                    for pg in PdfReader(file).pages: text += pg.extract_text() or ""
                elif file.name.endswith('.txt'): text += file.getvalue().decode("utf-8")
                elif file.name.endswith('.csv'): text += pd.read_csv(file).to_string()
            except: pass
    return text

def build_providers(typhoon_key, openrouter_key, ollama_url, ollama_model):
    """สร้าง list ของ provider ตามลำดับความน่าเชื่อถือ"""
    providers = []
    hdrs = {"HTTP-Referer":"https://streamlit.io/","X-Title":"PA Chat"}

    # 1. Ollama local — ถ้าเปิดใช้
    if ollama_url and ollama_model:
        providers.append(dict(
            name="🖥️ Local (Ollama)", key="ollama",
            base_url=ollama_url, model=ollama_model,
            extra_hdrs={}, ctx_limit=24000, out_tokens=2048
        ))

    # 2. Typhoon — reliable, ภาษาไทยดี
    if typhoon_key:
        providers.append(dict(
            name="☁️ Typhoon", key=typhoon_key,
            base_url="https://api.opentyphoon.ai/v1",
            model="typhoon-v2.5-30b-a3b-instruct",
            extra_hdrs={}, ctx_limit=40000, out_tokens=2048
        ))

    # 3-N. OpenRouter free models — หลายตัวเพื่อ fallback
    if openrouter_key:
        free_models = [
            ("🔵 Qwen3-8b",          "qwen/qwen3-8b:free"),
            ("🟢 DeepSeek-R1-0528",   "deepseek/deepseek-r1-0528:free"),
            ("🟡 Llama-3.1-8b",       "meta-llama/llama-3.1-8b-instruct:free"),
            ("🟠 Gemma-3-4b",         "google/gemma-3-4b-it:free"),
            ("🔴 Mistral-Nemo",       "mistralai/mistral-nemo:free"),
            ("⚪ Phi-3-mini",         "microsoft/phi-3-mini-128k-instruct:free"),
        ]
        for label, model in free_models:
            providers.append(dict(
                name=label, key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",
                model=model, extra_hdrs=hdrs,
                ctx_limit=10000, out_tokens=1024
            ))
    return providers

# ── Session Init ──────────────────────────────────────
def init_chat_state():
    ss = st.session_state
    ss.setdefault('chatbot_messages', [{"role":"assistant","content":"สวัสดีครับ PA Assistant พร้อมให้บริการครับ"}])
    ss.setdefault('file_context', "")
    ss.setdefault('last_processed_files', set())
    ss.setdefault('last_provider', "")
    ss.setdefault('use_ollama', False)
    ss.setdefault('ollama_url', "http://localhost:11434/v1")
    ss.setdefault('ollama_model', "typhoon2-8b")

init_chat_state()

# ── Sidebar settings ───────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("**⚙️ ตั้งค่า Local AI (Ollama)**")
    use_ollama = st.toggle("ใช้ Ollama (เครื่องตัวเอง)", value=st.session_state.use_ollama, key="toggle_ollama")
    st.session_state.use_ollama = use_ollama
    if use_ollama:
        st.session_state.ollama_url   = st.text_input("Ollama URL",   value=st.session_state.ollama_url,   key="inp_ollama_url")
        st.session_state.ollama_model = st.text_input("Model name",   value=st.session_state.ollama_model, key="inp_ollama_model")
        st.caption("ติดตั้ง Ollama: https://ollama.com\nแล้วรัน: `ollama pull typhoon2-8b`")

# ── File Upload ───────────────────────────────────────
with st.expander("📂 อัปโหลดเอกสาร (PDF, TXT, CSV)"):
    uploaded_files = st.file_uploader("เลือกไฟล์...", type=['pdf','txt','csv'], accept_multiple_files=True)

current_files_set = {f.name for f in uploaded_files} if uploaded_files else set()
if current_files_set != st.session_state.last_processed_files or \
   (not st.session_state.file_context and (uploaded_files or os.path.isdir("Doc"))):
    with st.spinner("กำลังประมวลผลเอกสาร..."):
        raw_text = extract_text_from_files(uploaded_files)
        if raw_text:
            st.session_state.file_context = raw_text
            st.session_state.last_processed_files = current_files_set
            st.success(f"✅ อ่านข้อมูลเรียบร้อย ({len(raw_text):,} ตัวอักษร)")
        else:
            st.warning("ยังไม่มีข้อมูลเอกสาร")

# แสดง provider ที่ใช้อยู่
if st.session_state.last_provider:
    st.caption(f"Provider ล่าสุด: {st.session_state.last_provider}")

# ── Chat UI ───────────────────────────────────────────
chat_container = st.container(height=450, border=True)
with chat_container:
    for msg in st.session_state.chatbot_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input("พิมพ์คำถามของคุณ...", key="chat_input_main"):
    st.session_state.chatbot_messages.append({"role":"user","content":prompt})
    with chat_container:
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            try:
                # ── API Keys ──────────────────────────────────
                try:    typhoon_key    = st.secrets["api_key"]
                except: typhoon_key    = ""
                try:    openrouter_key = st.secrets["openrouter_api_key"]
                except: openrouter_key = ""

                ollama_url   = st.session_state.ollama_url   if st.session_state.use_ollama else ""
                ollama_model = st.session_state.ollama_model if st.session_state.use_ollama else ""

                # ── Build provider list ───────────────────────
                providers = build_providers(typhoon_key, openrouter_key, ollama_url, ollama_model)

                if not providers:
                    placeholder.warning(
                        "⚠️ ไม่พบ API Key\n\n"
                        "กรุณาเพิ่มใน Streamlit Secrets:\n"
                        "- `api_key` = Typhoon API key\n"
                        "- `openrouter_api_key` = OpenRouter key\n\n"
                        "หรือเปิด **Ollama** ในเมนูซ้ายมือ"
                    )
                    st.stop()

                # ── Try each provider ─────────────────────────
                stream = None
                used_name = ""
                last_err  = None

                for p in providers:
                    try:
                        ctx = filter_relevant_content(
                            st.session_state.file_context, prompt,
                            max_chars=p["ctx_limit"]
                        ) or "ไม่พบข้อมูลในเอกสาร ตอบตามความรู้ทั่วไป"

                        sys_msg = (
                            "คุณคือ PA Assistant ผู้เชี่ยวชาญการตรวจสอบผลสัมฤทธิ์ภาครัฐ\n"
                            "ตอบคำถามโดยอ้างอิงเนื้อหาด้านล่าง "
                            "ถ้าไม่พบให้บอกว่า 'ไม่พบข้อมูลในเอกสารที่เกี่ยวข้อง'\n"
                            f"--- เนื้อหา ---\n{ctx}\n---------------"
                        )
                        msgs = [
                            {"role":"system", "content": sys_msg},
                            {"role":"user",   "content": prompt}
                        ]

                        c = OpenAI(api_key=p["key"], base_url=p["base_url"])
                        kwargs = dict(
                            model=p["model"], messages=msgs,
                            stream=True, max_tokens=p["out_tokens"]
                        )
                        if p["extra_hdrs"]:
                            kwargs["extra_headers"] = p["extra_hdrs"]

                        stream    = c.chat.completions.create(**kwargs)
                        used_name = p["name"]
                        break

                    except Exception as e:
                        last_err = e
                        # 429 rate-limit → รอ 1 วิ แล้ว try ตัวถัดไป
                        if "429" in str(e):
                            time.sleep(1)
                        continue

                if stream is None:
                    placeholder.error(
                        f"⚠️ ทุก provider ตอบไม่ได้ในขณะนี้\n\n"
                        f"Error ล่าสุด: `{last_err}`\n\n"
                        "💡 **แนะนำ:** เปิดใช้ Ollama (เครื่องตัวเอง) ในเมนูซ้ายมือ "
                        "เพื่อใช้งานได้โดยไม่ง้อ internet"
                    )
                    st.stop()

                # ── Stream response ───────────────────────────
                st.session_state.last_provider = used_name
                full_response = ""
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response += delta
                        placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)
                st.session_state.chatbot_messages.append(
                    {"role":"assistant","content":full_response})

            except Exception as e:
                placeholder.error(f"Error: {e}")

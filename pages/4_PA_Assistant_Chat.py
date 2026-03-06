import streamlit as st
import pandas as pd
from openai import OpenAI
import os, time, math
import numpy as np
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

# ══════════════════════════════════════════════════════
# RAG SYSTEM — Typhoon Embeddings
# ══════════════════════════════════════════════════════

CHUNK_SIZE    = 400   # ตัวอักษรต่อ chunk
CHUNK_OVERLAP = 80    # overlap ระหว่าง chunk
TOP_K         = 5     # จำนวน chunk ที่เลือกมาตอบ

def split_chunks(text: str, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP) -> list[str]:
    """แบ่งข้อความเป็น chunks มี overlap"""
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i:i+size])
        i += size - overlap
    return [c.strip() for c in chunks if c.strip()]

def cosine_sim(a: list, b: list) -> float:
    a, b = np.array(a), np.array(b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom else 0.0

@st.cache_data(show_spinner=False)
def get_embeddings_cached(texts_tuple: tuple, api_key: str) -> list:
    """เรียก Typhoon Embeddings API — cache ผลลัพธ์ไว้"""
    texts = list(texts_tuple)
    client = OpenAI(api_key=api_key, base_url="https://api.opentyphoon.ai/v1")
    # Typhoon รับ batch สูงสุด 100 ต่อครั้ง
    all_embeddings = []
    batch_size = 50
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        resp = client.embeddings.create(
            model="typhoon-text-embedding",
            input=batch
        )
        all_embeddings.extend([item.embedding for item in resp.data])
    return all_embeddings

def retrieve_chunks(query: str, chunks: list[str], chunk_embeddings: list,
                    api_key: str, top_k=TOP_K) -> str:
    """หา chunks ที่เกี่ยวข้องกับคำถามมากที่สุด"""
    # Embed คำถาม
    client = OpenAI(api_key=api_key, base_url="https://api.opentyphoon.ai/v1")
    resp = client.embeddings.create(
        model="typhoon-text-embedding",
        input=[query]
    )
    q_emb = resp.data[0].embedding

    # คำนวณ cosine similarity กับทุก chunk
    scores = [(cosine_sim(q_emb, emb), i) for i, emb in enumerate(chunk_embeddings)]
    scores.sort(reverse=True)

    # เลือก top_k chunks (เรียงตาม index เพื่อรักษาลำดับเนื้อหา)
    top_indices = sorted([idx for _, idx in scores[:top_k]])
    selected = [chunks[i] for i in top_indices]
    return "\n\n---\n\n".join(selected)

# fallback TF-IDF เมื่อไม่มี Typhoon key
def tfidf_retrieve(query: str, chunks: list[str], top_k=TOP_K) -> str:
    query_words = set(query.split())
    scored = []
    for i, chunk in enumerate(chunks):
        score = sum(chunk.count(w) for w in query_words)
        if i < 3: score += 0.5
        scored.append((score, i))
    scored.sort(reverse=True)
    top_indices = sorted([idx for _, idx in scored[:top_k]])
    return "\n\n---\n\n".join(chunks[i] for i in top_indices)

# ── Extract text ───────────────────────────────────────
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

# ── LLM Providers ─────────────────────────────────────
def build_providers(typhoon_key, openrouter_key, ollama_url, ollama_model):
    providers = []
    hdrs = {"HTTP-Referer":"https://streamlit.io/","X-Title":"PA Chat"}
    if ollama_url and ollama_model:
        providers.append(dict(name="🖥️ Local (Ollama)", key="ollama",
            base_url=ollama_url, model=ollama_model,
            extra_hdrs={}, out_tokens=2048))
    if typhoon_key:
        providers.append(dict(name="☁️ Typhoon", key=typhoon_key,
            base_url="https://api.opentyphoon.ai/v1",
            model="typhoon-v2.5-30b-a3b-instruct",
            extra_hdrs={}, out_tokens=2048))
    if openrouter_key:
        for label, model in [
            ("🔵 Qwen3-8b",        "qwen/qwen3-8b:free"),
            ("🟢 DeepSeek-R1",     "deepseek/deepseek-r1-0528:free"),
            ("🟡 Llama-3.1-8b",    "meta-llama/llama-3.1-8b-instruct:free"),
            ("🟠 Gemma-3-4b",      "google/gemma-3-4b-it:free"),
            ("🔴 Mistral-Nemo",    "mistralai/mistral-nemo:free"),
        ]:
            providers.append(dict(name=label, key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",
                model=model, extra_hdrs=hdrs, out_tokens=1024))
    return providers

# ── Session Init ──────────────────────────────────────
def init_state():
    ss = st.session_state
    ss.setdefault('chatbot_messages', [{"role":"assistant","content":"สวัสดีครับ PA Assistant พร้อมให้บริการครับ"}])
    ss.setdefault('file_context',        "")
    ss.setdefault('doc_chunks',          [])
    ss.setdefault('chunk_embeddings',    [])
    ss.setdefault('rag_ready',           False)
    ss.setdefault('last_processed_files', set())
    ss.setdefault('last_provider',       "")
    ss.setdefault('use_ollama',          False)
    ss.setdefault('ollama_url',          "http://localhost:11434/v1")
    ss.setdefault('ollama_model',        "typhoon2-8b")

init_state()

# ── Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("**⚙️ Local AI (Ollama)**")
    use_ollama = st.toggle("ใช้ Ollama", value=st.session_state.use_ollama, key="toggle_ollama")
    st.session_state.use_ollama = use_ollama
    if use_ollama:
        st.session_state.ollama_url   = st.text_input("URL",        value=st.session_state.ollama_url,   key="inp_url")
        st.session_state.ollama_model = st.text_input("Model name", value=st.session_state.ollama_model, key="inp_model")
        st.caption("https://ollama.com\n`ollama pull typhoon2-8b`")

# ── File Upload + RAG Index ────────────────────────────
with st.expander("📂 อัปโหลดเอกสาร (PDF, TXT, CSV)"):
    uploaded_files = st.file_uploader("เลือกไฟล์...", type=['pdf','txt','csv'], accept_multiple_files=True)

try:    typhoon_key    = st.secrets["api_key"]
except: typhoon_key    = ""
try:    openrouter_key = st.secrets["openrouter_api_key"]
except: openrouter_key = ""

current_files_set = {f.name for f in uploaded_files} if uploaded_files else set()
files_changed = current_files_set != st.session_state.last_processed_files
first_load    = not st.session_state.file_context and (uploaded_files or os.path.isdir("Doc"))

if files_changed or first_load:
    with st.spinner("📖 กำลังอ่านเอกสาร..."):
        raw_text = extract_text_from_files(uploaded_files)

    if raw_text:
        st.session_state.file_context = raw_text
        st.session_state.last_processed_files = current_files_set

        # แบ่ง chunks เสมอ
        chunks = split_chunks(raw_text)
        st.session_state.doc_chunks = chunks
        st.session_state.rag_ready  = False   # reset embeddings

        # สร้าง embeddings ถ้ามี Typhoon key
        if typhoon_key:
            with st.spinner(f"🔢 กำลังสร้าง Vector Index ({len(chunks)} chunks)..."):
                try:
                    embs = get_embeddings_cached(tuple(chunks), typhoon_key)
                    st.session_state.chunk_embeddings = embs
                    st.session_state.rag_ready = True
                    st.success(f"✅ RAG พร้อมใช้งาน! ({len(chunks)} chunks · Vector search)")
                except Exception as e:
                    st.warning(f"⚠️ สร้าง embedding ไม่ได้ ใช้ TF-IDF แทน: {e}")
                    st.session_state.rag_ready = False
        else:
            st.success(f"✅ อ่านเอกสารแล้ว ({len(raw_text):,} chars · {len(chunks)} chunks · TF-IDF mode)")
    else:
        st.warning("ยังไม่มีข้อมูลเอกสาร")

# แสดงสถานะ RAG + provider ล่าสุด
col_s1, col_s2 = st.columns(2)
with col_s1:
    if st.session_state.rag_ready:
        st.caption(f"🟢 Vector RAG · {len(st.session_state.doc_chunks)} chunks")
    elif st.session_state.doc_chunks:
        st.caption(f"🟡 TF-IDF RAG · {len(st.session_state.doc_chunks)} chunks")
    else:
        st.caption("⚪ ยังไม่มีเอกสาร")
with col_s2:
    if st.session_state.last_provider:
        st.caption(f"Provider: {st.session_state.last_provider}")

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
                ollama_url   = st.session_state.ollama_url   if st.session_state.use_ollama else ""
                ollama_model = st.session_state.ollama_model if st.session_state.use_ollama else ""
                providers    = build_providers(typhoon_key, openrouter_key, ollama_url, ollama_model)

                if not providers:
                    placeholder.warning(
                        "⚠️ ไม่พบ API Key\n\n"
                        "กรุณาเพิ่มใน Streamlit Secrets:\n"
                        "- `api_key` = Typhoon\n- `openrouter_api_key` = OpenRouter\n\n"
                        "หรือเปิด **Ollama** ในเมนูซ้ายมือ"
                    )
                    st.stop()

                # ── RAG: ดึง context ที่เกี่ยวข้อง ──────────────
                chunks = st.session_state.doc_chunks
                if chunks:
                    if st.session_state.rag_ready and st.session_state.chunk_embeddings:
                        # Vector search
                        try:
                            context = retrieve_chunks(
                                prompt, chunks,
                                st.session_state.chunk_embeddings,
                                typhoon_key, top_k=TOP_K
                            )
                            rag_mode = "vector"
                        except Exception:
                            context  = tfidf_retrieve(prompt, chunks, top_k=TOP_K)
                            rag_mode = "tfidf-fallback"
                    else:
                        # TF-IDF fallback
                        context  = tfidf_retrieve(prompt, chunks, top_k=TOP_K)
                        rag_mode = "tfidf"
                else:
                    context  = "ไม่พบข้อมูลในเอกสาร ตอบตามความรู้ทั่วไป"
                    rag_mode = "none"

                # context ที่ได้จาก RAG จะสั้นมาก (~2,000 chars) ปลอดภัยสำหรับทุก model
                sys_msg = (
                    "คุณคือ PA Assistant ผู้เชี่ยวชาญการตรวจสอบผลสัมฤทธิ์ภาครัฐ\n"
                    "ตอบคำถามโดยอ้างอิงเนื้อหาต่อไปนี้ "
                    "ถ้าไม่พบให้บอกว่า 'ไม่พบข้อมูลในเอกสารที่เกี่ยวข้อง'\n"
                    f"[RAG mode: {rag_mode}]\n"
                    f"--- เนื้อหาที่เกี่ยวข้อง ---\n{context}\n--------------------------"
                )
                msgs = [
                    {"role":"system","content":sys_msg},
                    {"role":"user",  "content":prompt}
                ]

                # ── ลอง provider ทีละตัว ──────────────────────
                stream, used_name, last_err = None, "", None
                for p in providers:
                    try:
                        c = OpenAI(api_key=p["key"], base_url=p["base_url"])
                        kwargs = dict(model=p["model"], messages=msgs,
                                      stream=True, max_tokens=p["out_tokens"])
                        if p["extra_hdrs"]:
                            kwargs["extra_headers"] = p["extra_hdrs"]
                        stream    = c.chat.completions.create(**kwargs)
                        used_name = p["name"]
                        break
                    except Exception as e:
                        last_err = e
                        if "429" in str(e): time.sleep(1)
                        continue

                if stream is None:
                    placeholder.error(
                        f"⚠️ ทุก provider ตอบไม่ได้\n\nError: `{last_err}`\n\n"
                        "💡 ลองเปิด Ollama ในเมนูซ้ายมือ"
                    )
                    st.stop()

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

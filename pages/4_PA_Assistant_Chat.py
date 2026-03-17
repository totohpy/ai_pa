# -*- coding: utf-8 -*-
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
    from ai_provider import render_provider_sidebar, get_openai_client_and_model, get_provider_display_name
except ImportError:
    def apply_theme(): pass
    SIDEBAR_HTML = ""
    def render_provider_sidebar(): pass
    def get_openai_client_and_model(page="default"): raise ImportError("ai_provider not found")
    def get_provider_display_name(): return "Unknown"

st.set_page_config(page_title="PA Assistant Chat", page_icon="💬", layout="wide")
apply_theme()

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    render_provider_sidebar()

st.title("💬 PA Assistant Chat")
st.markdown("ถาม-ตอบผู้ช่วยอัจฉริยะ อ้างอิงคู่มือการปฏิบัติงานและผลการตรวจสอบที่ผ่านมา")

# ══════════════════════════════════════════════════════
# RAG SYSTEM — TF-IDF
# ══════════════════════════════════════════════════════

CHUNK_SIZE    = 600
CHUNK_OVERLAP = 100
TOP_K         = 6

def split_chunks(text: str, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP) -> list[str]:
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i:i+size])
        i += size - overlap
    return [c.strip() for c in chunks if c.strip()]

def tfidf_retrieve(query: str, chunks: list[str], top_k=TOP_K) -> str:
    words   = [w for w in query.split() if len(w) > 1]
    bigrams = [words[i] + words[i+1] for i in range(len(words)-1)]
    scored  = []
    for i, chunk in enumerate(chunks):
        score = sum(chunk.count(w) * 1.0 for w in words)
        score += sum(chunk.count(bg) * 2.0 for bg in bigrams)
        if i < 5: score += 0.5
        scored.append((score, i))
    scored.sort(reverse=True)
    top_indices = sorted([idx for _, idx in scored[:top_k]])
    return "\n\n---\n\n".join(chunks[i] for i in top_indices)

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

# ── Session Init ──────────────────────────────────────
def init_state():
    ss = st.session_state
    ss.setdefault('chatbot_messages', [{"role":"assistant","content":"สวัสดีครับ PA Assistant พร้อมให้บริการครับ"}])
    ss.setdefault('file_context',         "")
    ss.setdefault('doc_chunks',           [])
    ss.setdefault('last_processed_files', set())
    ss.setdefault('last_provider',        "")

init_state()

# ── File Upload + RAG Index ────────────────────────────
with st.expander("📂 อัปโหลดเอกสาร (PDF, TXT, CSV)"):
    uploaded_files = st.file_uploader("เลือกไฟล์...", type=['pdf','txt','csv'], accept_multiple_files=True)

current_files_set = {f.name for f in uploaded_files} if uploaded_files else set()
files_changed = current_files_set != st.session_state.last_processed_files
first_load    = not st.session_state.file_context and (uploaded_files or os.path.isdir("Doc"))

if files_changed or first_load:
    with st.spinner("📖 กำลังอ่านข้อมูลในระบบ..."):
        raw_text = extract_text_from_files(uploaded_files)
    if raw_text:
        chunks = split_chunks(raw_text)
        st.session_state.file_context         = raw_text
        st.session_state.doc_chunks           = chunks
        st.session_state.last_processed_files = current_files_set
        st.success(f"✅ พร้อมใช้งาน! ({len(raw_text):,} chars · {len(chunks)} chunks)")
    else:
        st.warning("ยังไม่มีข้อมูลเอกสาร")

# แสดงสถานะ
col_s1, col_s2 = st.columns(2)
with col_s1:
    if st.session_state.doc_chunks:
        st.caption(f"🟢 คลังข้อมูลพร้อม · {len(st.session_state.doc_chunks)} chunks")
    else:
        st.caption("⚪ ยังไม่มีเอกสาร")
with col_s2:
    st.caption(f"Provider: {get_provider_display_name()}")

# ── Chat UI ───────────────────────────────────────────
chat_container = st.container(height=450, border=True)
with chat_container:
    for msg in st.session_state.chatbot_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input("พิมพ์คำถามของคุณ...", key="chat_input_main"):
    st.session_state.chatbot_messages.append({"role":"user","content":prompt})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            try:
                # ── RAG: ดึง context ──────────────────────────────
                chunks = st.session_state.doc_chunks
                context = (tfidf_retrieve(prompt, chunks, top_k=TOP_K)
                           if chunks else "ไม่พบข้อมูลในเอกสาร ตอบตามความรู้ทั่วไป")

                sys_msg = (
                    "คุณคือ PA Assistant ผู้เชี่ยวชาญการตรวจสอบผลสัมฤทธิ์และประสิทธิภาพการดำเนินงาน (Performance Audit)\n"
                    "ตอบคำถามโดยอ้างอิงเนื้อหาต่อไปนี้ "
                    "ถ้าไม่พบให้บอกว่า 'ไม่พบข้อมูลในเอกสารที่เกี่ยวข้อง' และให้เดาว่าคำถามอาจจะหมายถึงอย่างอื่นที่ใกล้เคียงกัน หรืออาจจะพิมพ์คำถามผิด\n"
                    f"--- เนื้อหาที่เกี่ยวข้อง ---\n{context}\n--------------------------"
                )
                msgs = [
                    {"role": "system", "content": sys_msg},
                    {"role": "user",   "content": prompt},
                ]

                # ── เรียก AI ตาม provider ──────────────────────────
                client, model = get_openai_client_and_model(page="chat")
                st.session_state.last_provider = get_provider_display_name()

                stream = client.chat.completions.create(
                    model=model,
                    messages=msgs,
                    stream=True,
                    max_tokens=2048,
                )

                full_response = ""
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response += delta
                        placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)
                st.session_state.chatbot_messages.append(
                    {"role": "assistant", "content": full_response}
                )

            except Exception as e:
                provider = get_provider_display_name()
                placeholder.error(
                    f"⚠️ ไม่สามารถเชื่อมต่อ AI ได้ ({provider})\n\n"
                    f"รายละเอียด: `{e}`\n\n"
                    "💡 กรุณาตรวจสอบ:\n"
                    "- Secrets: `api_key`, `vertex_project_id`, `vertex_sa_json`\n"
                    "- หรือเปลี่ยนเป็น Local / On-Premise ใน sidebar"
                )


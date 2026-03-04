import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from theme import apply_theme, SIDEBAR_HTML

st.set_page_config(page_title="PA Planning Studio", page_icon="⚖️", layout="wide")
apply_theme()

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)

st.markdown("""
<style>
.banner {
    background: linear-gradient(135deg, #7A2020 0%, #9e2c2c 55%, #621a1a 100%);
    border-radius: 16px; padding: 24px 28px; margin-bottom: 22px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 8px 32px rgba(122,32,32,0.2); position: relative; overflow: hidden;
}
.banner::before { content:''; position:absolute; top:-50px; right:-50px; width:180px; height:180px; background:rgba(255,255,255,0.05); border-radius:50%; }
.banner-title { font-size:22px; font-weight:700; color:#fff; font-family:'Noto Serif Thai',serif; margin-bottom:6px; }
.banner-desc  { font-size:14px; color:rgba(255,255,255,0.72); line-height:1.6; }
.banner-emblem { width:64px; height:64px; flex-shrink:0; background:rgba(255,255,255,0.12); border:1px solid rgba(255,255,255,0.18); border-radius:16px; display:flex; align-items:center; justify-content:center; position:relative; z-index:1; }
.banner-emblem svg { width:36px; height:36px; fill:#fff; }

/* AI pills */
.ai-pills { display:flex; align-items:center; gap:7px; flex-wrap:wrap; margin-bottom:20px; }
.ai-pill { display:inline-flex; align-items:center; gap:6px; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:600; border:1px solid; white-space:nowrap; background:#fff; font-family:'Sarabun',sans-serif; }
.ai-pill svg { width:13px; height:13px; flex-shrink:0; }
.pill-dot { width:6px; height:6px; border-radius:50%; flex-shrink:0; animation:blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }
.pill-onprem { border-color:rgba(122,32,32,0.28); color:#7A2020; }
.pill-onprem svg { fill:#7A2020; } .pill-onprem .pill-dot { background:#7A2020; }
.pill-cloud  { border-color:rgba(109,158,81,0.30); color:#4a7a32; }
.pill-cloud  svg { fill:#4a7a32; } .pill-cloud  .pill-dot { background:#6D9E51; }
.pill-local  { border-color:rgba(60,90,140,0.28); color:#3c5a8c; }
.pill-local  svg { fill:#3c5a8c; } .pill-local  .pill-dot { background:#3c5a8c; }

/* Section label */
.sec-lbl { font-size:11px; font-weight:700; color:#7A2020; letter-spacing:1.6px; text-transform:uppercase; margin-bottom:12px; display:flex; align-items:center; gap:8px; }
.sec-lbl::after { content:''; flex:1; height:1px; background:#e3e4c4; }

/* Feature cards */
.flink { text-decoration:none !important; color:inherit !important; display:block; }
.fcard {
    background:#fff; border:1px solid #d8d9b4; border-radius:16px; padding:22px;
    cursor:pointer; position:relative; overflow:hidden;
    box-shadow:0 1px 4px rgba(122,32,32,0.07);
    transition:all 0.25s cubic-bezier(.34,1.46,.64,1);
}
.fcard::after { content:''; position:absolute; bottom:0; left:0; right:0; height:3px; background:#7A2020; transform:scaleX(0); transform-origin:left; transition:transform 0.22s ease; }
.fcard:hover { box-shadow:0 8px 32px rgba(122,32,32,0.13); transform:translateY(-4px); }
.fcard:hover::after { transform:scaleX(1); }
.fcard-icon { width:46px; height:46px; border-radius:12px; background:rgba(122,32,32,0.08); border:1px solid rgba(122,32,32,0.12); display:flex; align-items:center; justify-content:center; margin-bottom:14px; }
.fcard-icon svg { width:24px; height:24px; fill:#7A2020; }
.fcard-title { font-size:15px; font-weight:700; color:#1a1a1a; margin-bottom:8px; font-family:'Noto Serif Thai',serif; }
.fcard-desc  { font-size:13px; color:#8a8a8a; line-height:1.65; }
.fcard-chip  { position:absolute; top:18px; right:18px; width:26px; height:26px; border-radius:7px; background:#e8f5e0; border:1px solid #BCD9A2; display:flex; align-items:center; justify-content:center; transition:all 0.2s; }
.fcard-chip svg { width:12px; height:12px; fill:#6D9E51; transition:all 0.2s; }
.fcard:hover .fcard-chip { background:#6D9E51; border-color:#6D9E51; transform:rotate(45deg); }
.fcard:hover .fcard-chip svg { fill:#fff; }

.infobox { background:#FEFFD3; border:1px solid #e0e098; border-left:4px solid #7A2020; border-radius:10px; padding:12px 16px; font-size:13px; color:#404040; line-height:1.6; display:flex; align-items:flex-start; gap:10px; margin-top:6px; }
.infobox svg { width:16px; height:16px; fill:#7A2020; flex-shrink:0; margin-top:1px; }
</style>
""", unsafe_allow_html=True)

# ── Banner ─────────────────────────────────────────────
st.markdown("""
<div class="banner">
  <div>
    <div class="banner-title">PA Planning Studio</div>
    <div class="banner-desc">
      เครื่องมืออัจฉริยะสำหรับการวางแผนและตรวจสอบผลสัมฤทธิ์ภาครัฐ<br>
      Audit Intelligence Team &nbsp;·&nbsp; PAO1 &nbsp;·&nbsp; สำนักงานการตรวจเงินแผ่นดิน
    </div>
  </div>
  <div class="banner-emblem">
    <svg viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 4l6 2.67V11c0 3.72-2.55 7.15-6 8.32-3.45-1.17-6-4.6-6-8.32V7.67L12 5z"/></svg>
  </div>
</div>
""", unsafe_allow_html=True)

# ── AI Mode Pills ──────────────────────────────────────
st.markdown("""
<div class="ai-pills">
  <div class="ai-pill pill-onprem">
    <div class="pill-dot"></div>
    <svg viewBox="0 0 24 24"><path d="M20 3H4v10c0 2.21 1.79 4 4 4h6c2.21 0 4-1.79 4-4v-3h2c1.11 0 2-.89 2-2V5c0-1.11-.89-2-2-2zm0 5h-2V5h2v3zM4 19h16v2H4z"/></svg>
    On-Premise AI
  </div>
  <div class="ai-pill pill-cloud">
    <div class="pill-dot"></div>
    <svg viewBox="0 0 24 24"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"/></svg>
    Cloud AI
  </div>
  <div class="ai-pill pill-local">
    <div class="pill-dot"></div>
    <svg viewBox="0 0 24 24"><path d="M4 6h18V4H4c-1.1 0-2 .9-2 2v11H0v3h14v-3H4V6zm19 2h-6c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h6c.55 0 1-.45 1-1V9c0-.55-.45-1-1-1zm-1 9h-4v-7h4v7z"/></svg>
    Local AI
  </div>
</div>
""", unsafe_allow_html=True)

# ── Main Tools ─────────────────────────────────────────
st.markdown('<div class="sec-lbl">เครื่องมือหลัก</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown("""<a href="Audit_Design_Assistant" target="_self" class="flink">
    <div class="fcard">
      <div class="fcard-icon"><svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11zM8 15h8v2H8zm0-4h8v2H8zm0-4h5v2H8z"/></svg></div>
      <div class="fcard-title">Audit Design Assistant</div>
      <div class="fcard-desc">วิเคราะห์แผน 6W2H · Logic Model · ค้นหาข้อตรวจพบ และแนะนำประเด็นด้วย AI</div>
      <div class="fcard-chip"><svg viewBox="0 0 24 24"><path d="M7 17L17 7M17 7H7M17 7v10"/></svg></div>
    </div></a>""", unsafe_allow_html=True)

with c2:
    st.markdown("""<a href="Audit_Plan_Generator" target="_self" class="flink">
    <div class="fcard">
      <div class="fcard-icon"><svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 11h-4v4h-4v-4H6v-4h4V6h4v4h4v4z"/></svg></div>
      <div class="fcard-title">Audit Plan Generator</div>
      <div class="fcard-desc">ร่างแผนและแนวการตรวจสอบ พร้อม AI สร้างเนื้อหาแต่ละส่วน ส่งออกเป็น Word / HTML</div>
      <div class="fcard-chip"><svg viewBox="0 0 24 24"><path d="M7 17L17 7M17 7H7M17 7v10"/></svg></div>
    </div></a>""", unsafe_allow_html=True)

with c3:
    st.markdown("""<a href="PA_Assistant_Chat" target="_self" class="flink">
    <div class="fcard">
      <div class="fcard-icon"><svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg></div>
      <div class="fcard-title">PA Assistant Chat</div>
      <div class="fcard-desc">ถาม-ตอบผู้ช่วยอัจฉริยะ อ้างอิงคู่มือและผลการตรวจสอบ รองรับ PDF · CSV · TXT</div>
      <div class="fcard-chip"><svg viewBox="0 0 24 24"><path d="M7 17L17 7M17 7H7M17 7v10"/></svg></div>
    </div></a>""", unsafe_allow_html=True)

# ── Utilities ──────────────────────────────────────────
st.markdown('<div class="sec-lbl" style="margin-top:8px">ยูทิลิตี้</div>', unsafe_allow_html=True)
u1, u2, u3 = st.columns(3, gap="medium")

with u1:
    st.markdown("""<a href="แปลงภาพเป็นข้อความ_(OCR)" target="_self" class="flink">
    <div class="fcard">
      <div class="fcard-icon"><svg viewBox="0 0 24 24"><path d="M9.5 6.5v3h-3v-3h3M11 5H5v6h6V5zm-1.5 9.5v3h-3v-3h3M11 13H5v6h6v-6zm6.5-6.5v3h-3v-3h3M19 5h-6v6h6V5zm-6 8h1.5v1.5H13V13zm1.5 1.5H16V16h-1.5v-1.5zM16 13h1.5v1.5H16V13zm-3 3h1.5v1.5H13V16zm1.5 1.5H16V19h-1.5v-1.5zM16 16h1.5v1.5H16V16zm1.5-1.5H19V16h-1.5v-1.5zm0 3H19V19h-1.5v-1.5z"/></svg></div>
      <div class="fcard-title">OCR – แปลงภาพเป็นข้อความ</div>
      <div class="fcard-desc">ดึงข้อความจากเอกสารภาษาไทย–อังกฤษด้วย Typhoon OCR AI</div>
      <div class="fcard-chip"><svg viewBox="0 0 24 24"><path d="M7 17L17 7M17 7H7M17 7v10"/></svg></div>
    </div></a>""", unsafe_allow_html=True)

with u2:
    st.markdown("""<a href="QR_Code_Generator" target="_self" class="flink">
    <div class="fcard">
      <div class="fcard-icon"><svg viewBox="0 0 24 24"><path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/></svg></div>
      <div class="fcard-title">QR Code Generator</div>
      <div class="fcard-desc">สร้าง QR Code พร้อมโลโก้หน่วยงาน รองรับโลโก้สีและขาว-ดำ</div>
      <div class="fcard-chip"><svg viewBox="0 0 24 24"><path d="M7 17L17 7M17 7H7M17 7v10"/></svg></div>
    </div></a>""", unsafe_allow_html=True)

with u3:
    st.markdown("""<a href="Audit_Dashboard" target="_self" class="flink">
    <div class="fcard">
      <div class="fcard-icon"><svg viewBox="0 0 24 24"><path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/></svg></div>
      <div class="fcard-title">Dashboard · Analytics</div>
      <div class="fcard-desc">Power BI · YData · Sweetviz · PyGWalker — วิเคราะห์ข้อมูลครบวงจร</div>
      <div class="fcard-chip"><svg viewBox="0 0 24 24"><path d="M7 17L17 7M17 7H7M17 7v10"/></svg></div>
    </div></a>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="infobox">
  <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
  <span>การใช้ฟีเจอร์ AI อาจผิดพลาดได้ โปรดตรวจสอบคำตอบอีกครั้ง และระบบจะแสดงข้อมูลขณะใช้งานเท่านั้น ไม่มีการจัดเก็บข้อมูลไว้</span>
</div>
""", unsafe_allow_html=True)

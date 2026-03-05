import streamlit as st
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from theme import apply_theme, SIDEBAR_HTML

st.set_page_config(page_title="PA Planning Studio", page_icon="⚖️", layout="wide")
apply_theme()

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)

st.markdown("""
<style>
/* ── Banner ── */
.banner {
    background: linear-gradient(135deg, #7A2020 0%, #9e2c2c 55%, #621a1a 100%);
    border-radius: 18px; padding: 26px 30px; margin-bottom: 24px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 10px 36px rgba(122,32,32,0.22); position: relative; overflow: hidden;
}
.banner::before { content:''; position:absolute; top:-60px; right:-60px; width:200px; height:200px; background:rgba(255,255,255,0.05); border-radius:50%; }
.banner::after  { content:''; position:absolute; bottom:-40px; left:120px; width:140px; height:140px; background:rgba(255,255,255,0.04); border-radius:50%; }
.banner-title { font-size:23px; font-weight:700; color:#fff; font-family:'Noto Serif Thai',serif; margin-bottom:7px; }
.banner-desc  { font-size:14px; color:rgba(255,255,255,0.75); line-height:1.65; }
.banner-emblem { width:68px; height:68px; flex-shrink:0; background:rgba(255,255,255,0.14); border:1px solid rgba(255,255,255,0.22); border-radius:18px; display:flex; align-items:center; justify-content:center; position:relative; z-index:1; font-size:34px; }

/* ── AI Pills ── */
.ai-pills { display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:22px; }
.ai-pill { display:inline-flex; align-items:center; gap:6px; padding:6px 15px; border-radius:20px; font-size:13px; font-weight:600; border:1px solid; white-space:nowrap; background:#fff; font-family:'Sarabun',sans-serif; }
.pill-dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; animation:blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.25} }
.pill-onprem { border-color:rgba(122,32,32,0.28); color:#7A2020; }
.pill-onprem .pill-dot { background:#7A2020; }
.pill-cloud  { border-color:rgba(109,158,81,0.30); color:#4a7a32; }
.pill-cloud  .pill-dot { background:#6D9E51; }
.pill-local  { border-color:rgba(60,90,140,0.28); color:#3c5a8c; }
.pill-local  .pill-dot { background:#3c5a8c; }

/* ── Section label ── */
.sec-lbl { font-size:11px; font-weight:700; color:#7A2020; letter-spacing:1.8px; text-transform:uppercase; margin-bottom:14px; display:flex; align-items:center; gap:10px; }
.sec-lbl::after { content:''; flex:1; height:1px; background:#e3e4c4; }

/* ══════════════════════════════════════
   MAIN TOOL CARDS — bigger, bolder
   ══════════════════════════════════════ */
.fcard-main {
    background:#fff;
    border:1.5px solid #d8d9b4;
    border-radius:18px;
    padding:26px 22px 22px;
    cursor:pointer;
    position:relative;
    overflow:hidden;
    box-shadow:0 2px 10px rgba(122,32,32,0.08);
    transition:all 0.28s cubic-bezier(.34,1.46,.64,1);
    height:100%;
}
.fcard-main::before {
    content:'';
    position:absolute; top:0; left:0; right:0; height:4px;
    background: linear-gradient(90deg, #7A2020, #c0392b);
    transform:scaleX(0); transform-origin:left;
    transition:transform 0.22s ease;
}
.fcard-main:hover {
    box-shadow:0 12px 40px rgba(122,32,32,0.16);
    transform:translateY(-6px);
    border-color:#b8a0a0;
}
.fcard-main:hover::before { transform:scaleX(1); }
.fcard-main-icon {
    width:54px; height:54px; border-radius:14px;
    background:rgba(122,32,32,0.09); border:1px solid rgba(122,32,32,0.14);
    display:flex; align-items:center; justify-content:center;
    margin-bottom:16px; font-size:26px;
}
.fcard-main-title { font-size:16px; font-weight:700; color:#1a1a1a; margin-bottom:9px; font-family:'Noto Serif Thai',serif; }
.fcard-main-desc  { font-size:13.5px; color:#666; line-height:1.7; }
.fcard-main-badge {
    position:absolute; top:18px; right:18px;
    background:#7A2020; color:#fff;
    font-size:10px; font-weight:700; letter-spacing:1px;
    padding:3px 9px; border-radius:20px; text-transform:uppercase;
}

/* ── Utility cards ── */
.fcard-util {
    background:#fff; border:1px solid #d8d9b4; border-radius:14px; padding:18px;
    cursor:pointer; position:relative; overflow:hidden;
    box-shadow:0 1px 5px rgba(122,32,32,0.06);
    transition:all 0.22s cubic-bezier(.34,1.46,.64,1); height:100%;
}
.fcard-util::after { content:''; position:absolute; bottom:0; left:0; right:0; height:2.5px; background:#7A2020; transform:scaleX(0); transform-origin:left; transition:transform 0.2s ease; }
.fcard-util:hover { box-shadow:0 6px 24px rgba(122,32,32,0.12); transform:translateY(-4px); }
.fcard-util:hover::after { transform:scaleX(1); }
.fcard-util-icon { width:40px; height:40px; border-radius:10px; background:rgba(122,32,32,0.07); border:1px solid rgba(122,32,32,0.11); display:flex; align-items:center; justify-content:center; margin-bottom:12px; font-size:20px; }
.fcard-util-title { font-size:14px; font-weight:700; color:#1a1a1a; margin-bottom:7px; font-family:'Noto Serif Thai',serif; }
.fcard-util-desc  { font-size:12.5px; color:#7a7a7a; line-height:1.65; }

/* ── Info box ── */
.infobox { background:#FEFFD3; border:1px solid #e0e098; border-left:4px solid #7A2020; border-radius:10px; padding:12px 16px; font-size:13px; color:#404040; line-height:1.6; margin-top:8px; }

/* ── Nav button overrides ── */
.stButton>button { text-align:left !important; border-radius:0 0 14px 14px !important; border-top:none !important; border:1px solid #e0e0c8 !important; font-size:13px !important; color:#7A2020 !important; background:#fafaf5 !important; padding:8px 16px !important; font-weight:600 !important; }
.stButton>button:hover { background:#7A2020 !important; color:#fff !important; }
</style>
""", unsafe_allow_html=True)

# ── Banner ──────────────────────────────────────────
st.markdown("""
<div class="banner">
  <div style="position:relative;z-index:1;">
    <div class="banner-title">PA Planning Studio</div>
    <div class="banner-desc">
      เครื่องมืออัจฉริยะสำหรับการวางแผนและตรวจสอบผลสัมฤทธิ์ภาครัฐ<br>
      Audit Intelligence Team &nbsp;·&nbsp; PAO1 &nbsp;·&nbsp; สำนักงานการตรวจเงินแผ่นดิน
    </div>
  </div>
  <div class="banner-emblem">⚖️</div>
</div>
""", unsafe_allow_html=True)

# ── AI Pills ────────────────────────────────────────
st.markdown("""
<div class="ai-pills">
  <div class="ai-pill pill-onprem"><div class="pill-dot"></div>🖥️ On-Premise AI</div>
  <div class="ai-pill pill-cloud"><div class="pill-dot"></div>☁️ Cloud AI</div>
  <div class="ai-pill pill-local"><div class="pill-dot"></div>💻 Local AI</div>
</div>
""", unsafe_allow_html=True)

# ══ MAIN TOOLS ═══════════════════════════════════════
st.markdown('<div class="sec-lbl">เครื่องมือหลัก</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown("""
    <div class="fcard-main">
      <div class="fcard-main-badge">AI</div>
      <div class="fcard-main-icon">📋</div>
      <div class="fcard-main-title">Audit Design Assistant</div>
      <div class="fcard-main-desc">วิเคราะห์แผน 6W2H · Logic Model · Flowchart<br>ค้นหาข้อตรวจพบเดิม และแนะนำประเด็นด้วย AI</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("เปิด Audit Design Assistant →", key="go_1", use_container_width=True):
        st.switch_page("pages/2_Audit_Design_Assistant.py")

with c2:
    st.markdown("""
    <div class="fcard-main">
      <div class="fcard-main-badge">AI</div>
      <div class="fcard-main-icon">🔮</div>
      <div class="fcard-main-title">Audit Plan Generator</div>
      <div class="fcard-main-desc">ร่างแผนและแนวการตรวจสอบอัตโนมัติ<br>AI สร้างเนื้อหา ส่งออก Word / HTML ได้ทันที</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("เปิด Audit Plan Generator →", key="go_2", use_container_width=True):
        st.switch_page("pages/3_Audit_Plan_Generator.py")

with c3:
    st.markdown("""
    <div class="fcard-main">
      <div class="fcard-main-badge">AI</div>
      <div class="fcard-main-icon">💬</div>
      <div class="fcard-main-title">PA Assistant Chat</div>
      <div class="fcard-main-desc">ถาม-ตอบผู้ช่วยอัจฉริยะ อ้างอิงคู่มือ<br>และผลการตรวจสอบ รองรับ PDF · CSV · TXT</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("เปิด PA Assistant Chat →", key="go_3", use_container_width=True):
        st.switch_page("pages/4_PA_Assistant_Chat.py")

# ══ UTILITY TOOLS (4 หน้า) ═══════════════════════════
st.markdown('<div class="sec-lbl" style="margin-top:22px;">ยูทิลิตี้</div>', unsafe_allow_html=True)

u1, u2, u3, u4 = st.columns(4, gap="medium")

with u1:
    st.markdown("""
    <div class="fcard-util">
      <div class="fcard-util-icon">📄</div>
      <div class="fcard-util-title">OCR – แปลงภาพเป็นข้อความ</div>
      <div class="fcard-util-desc">ดึงข้อความจากเอกสารภาษาไทย–อังกฤษด้วย Typhoon OCR AI ถ่ายรูปหรืออัปโหลดได้เลย</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("เปิด OCR →", key="go_4", use_container_width=True):
        st.switch_page("pages/5_แปลงภาพเป็นข้อความ_(OCR).py")

with u2:
    st.markdown("""
    <div class="fcard-util">
      <div class="fcard-util-icon">📱</div>
      <div class="fcard-util-title">QR Code Generator</div>
      <div class="fcard-util-desc">สร้าง QR Code พร้อมโลโก้หน่วยงาน รองรับโลโก้สี และขาว-ดำ ดาวน์โหลด PNG ได้ทันที</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("เปิด QR Code Generator →", key="go_5", use_container_width=True):
        st.switch_page("pages/6_QR_Code_Generator.py")

with u3:
    st.markdown("""
    <div class="fcard-util">
      <div class="fcard-util-icon">📊</div>
      <div class="fcard-util-title">Audit Dashboard</div>
      <div class="fcard-util-desc">อัปโหลดข้อมูล สร้าง Dashboard อัตโนมัติ สั่งด้วย AI หรือเลือก Template สำเร็จรูป</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("เปิด Audit Dashboard →", key="go_6", use_container_width=True):
        st.switch_page("pages/7_Audit_Dashboard.py")

with u4:
    st.markdown("""
    <div class="fcard-util">
      <div class="fcard-util-icon">🕵️</div>
      <div class="fcard-util-title">Analytics Sandbox</div>
      <div class="fcard-util-desc">Power BI Mode · YData · Sweetviz · PyGWalker วิเคราะห์ข้อมูลเชิงลึกครบวงจร</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("เปิด Analytics Sandbox →", key="go_7", use_container_width=True):
        st.switch_page("pages/8_Analytics_Sandbox.py")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="infobox">⚠️ การใช้ฟีเจอร์ AI อาจผิดพลาดได้ โปรดตรวจสอบคำตอบอีกครั้ง และระบบจะแสดงข้อมูลขณะใช้งานเท่านั้น ไม่มีการจัดเก็บข้อมูลไว้</div>', unsafe_allow_html=True)

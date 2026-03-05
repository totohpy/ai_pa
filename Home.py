import streamlit as st
import sys, os, pathlib

_here = pathlib.Path(__file__).resolve().parent
for _p in [_here, pathlib.Path(os.getcwd())]:
    if (_p / "theme.py").exists():
        if str(_p) not in sys.path: sys.path.insert(0, str(_p))
        break
try:
    from theme import apply_theme, SIDEBAR_HTML
except ImportError:
    def apply_theme(): pass
    SIDEBAR_HTML = ""

st.set_page_config(page_title="PA Planning Studio", page_icon="🔎", layout="wide")
apply_theme()

# ── AI Mode state ─────────────────────────────────────
if "ai_mode" not in st.session_state:
    st.session_state.ai_mode = "cloud"   # "cloud" | "local"

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)

# ── Page CSS ──────────────────────────────────────────
st.markdown("""
<style>
/* Banner */
.banner {
    background:linear-gradient(135deg,#7A2020 0%,#9e2c2c 55%,#5a1515 100%);
    border-radius:18px; padding:28px 32px 24px; margin-bottom:22px;
    display:flex; align-items:center; justify-content:space-between;
    box-shadow:0 10px 36px rgba(122,32,32,0.22); position:relative; overflow:hidden;
}
.banner::before {
    content:''; position:absolute; top:-70px; right:-70px;
    width:220px; height:220px; background:rgba(255,255,255,0.04); border-radius:50%;
}
.banner::after {
    content:''; position:absolute; bottom:-50px; left:30%;
    width:160px; height:160px; background:rgba(255,255,255,0.03); border-radius:50%;
}
.banner-title {
    font-size:22px; font-weight:700; color:#fff;
    font-family:'Noto Serif Thai',serif; margin-bottom:6px; position:relative; z-index:1;
}
.banner-desc { font-size:13.5px; color:rgba(255,255,255,0.76); line-height:1.7; position:relative; z-index:1; }
.banner-icon {
    width:72px; height:72px; flex-shrink:0;
    background:rgba(255,255,255,0.12); border:1px solid rgba(255,255,255,0.2);
    border-radius:20px; display:flex; align-items:center; justify-content:center;
    font-size:38px; position:relative; z-index:1;
}

/* AI Mode Switcher */
.ai-switcher-wrap {
    display:flex; align-items:center; gap:12px; margin-bottom:20px;
    background:#fff; border:1px solid #d8d9b4; border-radius:14px;
    padding:10px 16px;
}
.ai-sw-label { font-size:12px; font-weight:700; color:#7a7a7a; text-transform:uppercase; letter-spacing:0.8px; white-space:nowrap; }
.ai-sw-pills { display:flex; gap:6px; }
.ai-pill-btn {
    display:inline-flex; align-items:center; gap:5px;
    padding:5px 14px; border-radius:20px; font-size:12.5px; font-weight:600;
    cursor:pointer; border:1.5px solid transparent; transition:all 0.18s;
    font-family:'Sarabun',sans-serif; text-decoration:none;
}
.ai-pill-active   { background:#7A2020; color:#fff; border-color:#7A2020; }
.ai-pill-inactive { background:#f8f9ee; color:#7a7a7a; border-color:#d8d9b4; }
.ai-pill-inactive:hover { border-color:#7A2020; color:#7A2020; }
.pill-dot { width:6px; height:6px; border-radius:50%; background:currentColor; opacity:0.7; }
.ai-status-dot { width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:6px; animation:blink 2s infinite; }
.dot-cloud { background:#6D9E51; }
.dot-local { background:#3c5a8c; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }
.ai-current-label { font-size:12px; color:#404040; display:flex; align-items:center; margin-left:auto; }

/* Section label */
.sec-lbl {
    font-size:11px; font-weight:700; color:#7A2020; letter-spacing:1.8px;
    text-transform:uppercase; margin-bottom:14px; display:flex; align-items:center; gap:10px;
}
.sec-lbl::after { content:''; flex:1; height:1px; background:#e3e4c4; }

/* Main cards */
a.fcard-link { text-decoration:none !important; color:inherit !important; display:block; height:100%; }
.fcard-main {
    background:#fff; border:1.5px solid #d8d9b4; border-radius:18px;
    padding:22px 20px 18px; position:relative; overflow:hidden; height:100%;
    box-shadow:0 2px 10px rgba(122,32,32,0.06);
    transition:all 0.26s cubic-bezier(.34,1.46,.64,1);
}
.fcard-main::before {
    content:''; position:absolute; top:0; left:0; right:0; height:4px;
    background:linear-gradient(90deg,#7A2020,#c0392b);
    transform:scaleX(0); transform-origin:left; transition:transform 0.22s ease;
}
a.fcard-link:hover .fcard-main { box-shadow:0 12px 40px rgba(122,32,32,0.14); transform:translateY(-6px); border-color:#b8a0a0; }
a.fcard-link:hover .fcard-main::before { transform:scaleX(1); }
.fcard-corner {
    position:absolute; top:14px; right:14px;
    width:32px; height:32px; border-radius:10px;
    background:rgba(122,32,32,0.07); border:1px solid rgba(122,32,32,0.12);
    display:flex; align-items:center; justify-content:center; font-size:16px;
}
.fcard-icon  {
    width:50px; height:50px; border-radius:14px;
    background:rgba(122,32,32,0.08); border:1px solid rgba(122,32,32,0.13);
    display:flex; align-items:center; justify-content:center; margin-bottom:13px; font-size:24px;
}
.fcard-title { font-size:15px; font-weight:700; color:#1a1a1a; margin-bottom:7px; font-family:'Noto Serif Thai',serif; }
.fcard-desc  { font-size:13px; color:#666; line-height:1.7; }

/* Utility cards — 4x1 row */
.fcard-util {
    background:#fff; border:1px solid #d8d9b4; border-radius:14px;
    padding:16px 16px 14px; position:relative; overflow:hidden; height:100%;
    box-shadow:0 1px 5px rgba(122,32,32,0.04);
    transition:all 0.22s cubic-bezier(.34,1.46,.64,1);
}
.fcard-util::after {
    content:''; position:absolute; bottom:0; left:0; right:0; height:3px;
    background:#7A2020; transform:scaleX(0); transform-origin:left; transition:transform 0.2s ease;
}
a.fcard-link:hover .fcard-util { box-shadow:0 6px 24px rgba(122,32,32,0.12); transform:translateY(-4px); }
a.fcard-link:hover .fcard-util::after { transform:scaleX(1); }
.fcard-util-icon  {
    width:38px; height:38px; border-radius:10px;
    background:rgba(122,32,32,0.07); border:1px solid rgba(122,32,32,0.10);
    display:flex; align-items:center; justify-content:center; margin-bottom:10px; font-size:19px;
}
.fcard-util-title { font-size:13.5px; font-weight:700; color:#1a1a1a; margin-bottom:5px; font-family:'Noto Serif Thai',serif; }
.fcard-util-desc  { font-size:12px; color:#7a7a7a; line-height:1.6; }

.infobox {
    background:#FEFFD3; border:1px solid #e0e098; border-left:4px solid #7A2020;
    border-radius:10px; padding:11px 16px; font-size:13px; color:#404040;
    line-height:1.6; margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# ── Banner ────────────────────────────────────────────
st.markdown("""
<div class="banner">
  <div style="position:relative;z-index:1;">
    <div class="banner-title">Performance Audit Planning Studio</div>
    <div class="banner-desc">
      เครื่องมืออัจฉริยะสำหรับการตรวจสอบผลสัมฤทธิ์และประสิทธิภาพดำเนินงาน<br>
      Audit Intelligence Team &nbsp;·&nbsp; PAO1 &nbsp;·&nbsp; สำนักงานการตรวจเงินแผ่นดิน
    </div>
  </div>
  <div class="banner-icon">🔎</div>
</div>
""", unsafe_allow_html=True)

# ── AI Mode Switcher (interactive via st.button) ──────
col_sw, col_gap = st.columns([3, 7])
with col_sw:
    with st.container(border=True):
        st.markdown("**⚙️ เลือกโหมด AI**")
        c1, c2 = st.columns(2)
        with c1:
            cloud_type  = "primary"   if st.session_state.ai_mode == "cloud" else "secondary"
            if st.button("☁️  Cloud AI", key="btn_cloud", type=cloud_type, use_container_width=True):
                st.session_state.ai_mode = "cloud"
                st.rerun()
        with c2:
            local_type  = "primary"   if st.session_state.ai_mode == "local" else "secondary"
            if st.button("💻  Local AI", key="btn_local", type=local_type, use_container_width=True):
                st.session_state.ai_mode = "local"
                st.rerun()

        if st.session_state.ai_mode == "cloud":
            st.markdown('<div style="font-size:12px;color:#6D9E51;margin-top:4px;">🟢 ใช้ Typhoon API (Cloud)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:12px;color:#3c5a8c;margin-top:4px;">🔵 ใช้ Local Model (Ollama)</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Main Tools (3 cards) ──────────────────────────────
st.markdown('<div class="sec-lbl">เครื่องมือหลัก</div>', unsafe_allow_html=True)
m1, m2, m3 = st.columns(3, gap="medium")

with m1:
    st.markdown("""
    <a class="fcard-link" href="Audit_Design_Assistant" target="_self">
      <div class="fcard-main">
        <div class="fcard-corner">📋</div>
        <div class="fcard-icon">🏳️</div>
        <div class="fcard-title">Audit Design Assistant</div>
        <div class="fcard-desc">วิเคราะห์แผน 6W2H · Logic Model · Flowchart ค้นหาข้อตรวจพบเดิม และแนะนำประเด็นด้วย AI</div>
      </div>
    </a>""", unsafe_allow_html=True)

with m2:
    st.markdown("""
    <a class="fcard-link" href="Audit_Plan_Generator" target="_self">
      <div class="fcard-main">
        <div class="fcard-corner">📄</div>
        <div class="fcard-icon">🔮</div>
        <div class="fcard-title">Audit Plan Generator</div>
        <div class="fcard-desc">ร่างแผนและแนวการตรวจสอบอัตโนมัติ AI สร้างเนื้อหา ส่งออก Word / HTML ได้ทันที</div>
      </div>
    </a>""", unsafe_allow_html=True)

with m3:
    st.markdown("""
    <a class="fcard-link" href="PA_Assistant_Chat" target="_self">
      <div class="fcard-main">
        <div class="fcard-corner">💬</div>
        <div class="fcard-icon">🤖</div>
        <div class="fcard-title">PA Assistant Chat</div>
        <div class="fcard-desc">ถาม-ตอบผู้ช่วยอัจฉริยะ อ้างอิงคู่มือและผลการตรวจสอบ รองรับ PDF · CSV · TXT</div>
      </div>
    </a>""", unsafe_allow_html=True)

# ── Utility Tools (4x1 row) ───────────────────────────
st.markdown('<div class="sec-lbl" style="margin-top:24px;">ยูทิลิตี้</div>', unsafe_allow_html=True)
u1, u2, u3, u4 = st.columns(4, gap="medium")

with u1:
    st.markdown("""
    <a class="fcard-link" href="แปลงภาพเป็นข้อความ_(OCR)" target="_self">
      <div class="fcard-util">
        <div class="fcard-util-icon">📄</div>
        <div class="fcard-util-title">OCR แปลงภาพเป็นข้อความ</div>
        <div class="fcard-util-desc">ดึงข้อความจากเอกสารภาษาไทย–อังกฤษด้วย Typhoon OCR</div>
      </div>
    </a>""", unsafe_allow_html=True)

with u2:
    st.markdown("""
    <a class="fcard-link" href="QR_Code_Generator" target="_self">
      <div class="fcard-util">
        <div class="fcard-util-icon">📱</div>
        <div class="fcard-util-title">QR Code Generator</div>
        <div class="fcard-util-desc">สร้าง QR Code พร้อมโลโก้หน่วยงาน ดาวน์โหลด PNG ได้ทันที</div>
      </div>
    </a>""", unsafe_allow_html=True)

with u3:
    st.markdown("""
    <a class="fcard-link" href="Audit_Dashboard" target="_self">
      <div class="fcard-util">
        <div class="fcard-util-icon">📊</div>
        <div class="fcard-util-title">Audit Dashboard</div>
        <div class="fcard-util-desc">Dashboard สรุปสภาพปัญหาด้านสิ่งแวดล้อมและการวางแผนตรวจสอบ</div>
      </div>
    </a>""", unsafe_allow_html=True)

with u4:
    st.markdown("""
    <a class="fcard-link" href="Analytics_Sandbox" target="_self">
      <div class="fcard-util">
        <div class="fcard-util-icon">🕵️</div>
        <div class="fcard-util-title">Analytics Sandbox</div>
        <div class="fcard-util-desc">Power BI Mode · YData · Sweetviz · PyGWalker วิเคราะห์ข้อมูลเชิงลึก</div>
      </div>
    </a>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="infobox">⚠️ การใช้ฟีเจอร์ AI อาจผิดพลาดได้ โปรดตรวจสอบคำตอบอีกครั้ง ระบบไม่มีการจัดเก็บข้อมูลไว้</div>', unsafe_allow_html=True)

import streamlit as st
import sys, os, pathlib

_here = pathlib.Path(__file__).resolve().parent
for _p in [_here, pathlib.Path(os.getcwd())]:
    if (_p / "theme.py").exists():
        if str(_p) not in sys.path: sys.path.insert(0, str(_p))
        break
try:
    from theme import apply_theme, SIDEBAR_HTML
    from ai_provider import render_provider_sidebar
except ImportError:
    def apply_theme(): pass
    SIDEBAR_HTML = ""
    def render_provider_sidebar(): pass

st.set_page_config(
    page_title="ระบบอัจฉริยะสำหรับการตรวจสอบผลสัมฤทธิ์และประสิทธิภาพดำเนินงาน · Performance Audit Planning Studio",
    page_icon="🧭", layout="wide"
)
apply_theme()

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    render_provider_sidebar()

st.markdown("""
<style>
/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #501313 0%, #791F1F 45%, #A32D2D 100%);
    border-radius: 20px; padding: 36px 40px 32px; margin-bottom: 28px;
    position: relative; overflow: hidden;
}
.hero-grid {
    position: absolute; inset: 0; opacity: 0.04;
    background-image:
        repeating-linear-gradient(0deg, transparent, transparent 39px, #fff 39px, #fff 40px),
        repeating-linear-gradient(90deg, transparent, transparent 39px, #fff 39px, #fff 40px);
}
.hero-accent  { position: absolute; right: -40px; top: -40px;   width: 200px; height: 200px; border-radius: 50%; background: rgba(255,255,255,0.05); }
.hero-accent2 { position: absolute; right: 80px;  bottom: -60px; width: 140px; height: 140px; border-radius: 50%; background: rgba(255,255,200,0.03); }

.hero-badge {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(255,255,255,0.11); border: 1px solid rgba(255,255,255,0.18);
    border-radius: 100px; padding: 5px 13px; font-size: 11px;
    color: rgba(255,255,255,0.88); letter-spacing: 0.6px;
    margin-bottom: 14px; position: relative; z-index: 1;
}
.hero-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #4caf50; flex-shrink: 0;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.45; transform: scale(0.8); }
}
.hero-sep { width: 1px; height: 11px; background: rgba(255,255,255,0.25); flex-shrink: 0; }

.hero-title {
    font-size: 32px; font-weight: 700; color: #fff;
    position: relative; z-index: 1; margin-bottom: 8px; line-height: 1.3;
    white-space: nowrap;
}
.hero-title span {
    display: inline;
    background: linear-gradient(90deg, #fff, rgba(255,255,255,0.72));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub {
    font-size: 18px; color: rgba(255,255,255,0.62);
    line-height: 1.7; position: relative; z-index: 1; max-width: 520px;
    white-space: nowrap;
}

/* ── Section label ── */
.sec {
    margin-bottom: 12px; display: flex; align-items: center; gap: 10px;
}
.sec-title {
    font-size: 13px; font-weight: 600; color: #888;
    letter-spacing: 2px; text-transform: uppercase; white-space: nowrap;
}
.sec-line { flex: 1; height: 1px; background: #e5e5e5; }

/* ── Links ── */
a.hcard-link { text-decoration: none !important; color: inherit !important; display: block; height: 100%; }

/* ── Main cards ── */
.mcard {
    background: #fff; border: 0.5px solid #e0e0e0;
    border-radius: 14px; padding: 22px 20px 20px;
    position: relative; overflow: hidden; height: 100%;
    transition: transform .22s, border-color .22s;
}
.mcard-grid {
    position: absolute; inset: 0; pointer-events: none; overflow: hidden;
}
.mcard-grid::before {
    content: ''; position: absolute; top: -80px; right: -80px;
    width: 180px; height: 180px; border-radius: 50%;
    background: rgba(76, 175, 80, 0.06);
}
.mcard-grid::after {
    content: ''; position: absolute; top: 20px; right: -20px;
    width: 240px; height: 240px; border-radius: 50%;
    background: rgba(129, 199, 132, 0.08);
}
a.hcard-link:hover .mcard              { transform: translateY(-4px); border-color: #c8c8c8; }
a.hcard-link:hover .mcard .mcard-stripe{ transform: scaleX(1); }

.mcard-stripe {
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #791F1F, #E24B4A);
    transform: scaleX(0); transform-origin: left; transition: transform .24s ease;
}

.mcard-icon {
    width: 46px; height: 46px; border-radius: 12px;
    background: #f7f7f7; border: 0.5px solid #e5e5e5;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; margin-bottom: 14px; position: relative; z-index: 1;
}
.mcard-title { font-size: 15px; font-weight: 700; color: #1a1a1a; margin-bottom: 6px;  position: relative; z-index: 1; font-family: 'Noto Serif Thai', serif; }
.mcard-desc  { font-size: 13px; color: #666;     line-height: 1.65; position: relative; z-index: 1; }

/* ── Utility cards ── */
.ucard {
    background: #fff; border: 0.5px solid #e0e0e0;
    border-radius: 14px; padding: 16px 16px 15px;
    position: relative; overflow: hidden; height: 100%;
    transition: transform .2s, border-color .2s;
}
a.hcard-link:hover .ucard             { transform: translateY(-3px); border-color: #c8c8c8; }
a.hcard-link:hover .ucard .ucard-bar  { transform: scaleX(1); }

.ucard-bar {
    position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #185FA5, #378ADD);
    transform: scaleX(0); transform-origin: left; transition: transform .22s ease;
}
.ucard-icon {
    width: 34px; height: 34px; border-radius: 8px;
    background: #f7f7f7;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; margin-bottom: 10px;
}
.ucard-title { font-size: 14px;   font-weight: 700; color: #1a1a1a; margin-bottom: 4px; font-family: 'Noto Serif Thai', serif; }
.ucard-desc  { font-size: 12px; color: #888;      line-height: 1.6; }

/* ── Notice ── */
.infobox {
    display: flex; align-items: flex-start; gap: 8px;
    background: #FEFFD3; border: 0.5px solid #e0e098; border-left: 3px solid #7A2020;
    border-radius: 10px; padding: 10px 14px; margin-top: 8px;
    font-size: 14px; color: #555; line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-grid"></div>
  <div class="hero-accent"></div>
  <div class="hero-accent2"></div>
  <div class="hero-badge">
    <div class="hero-dot"></div>
    AI-Powered
    <div class="hero-sep"></div>
    Auditor-Driven
  </div>
  <div class="hero-title">
    <span>Performance Audit Planning Studio</span>
  </div>
  <div class="hero-sub">เครื่องมืออัจฉริยะสำหรับการตรวจสอบผลสัมฤทธิ์และประสิทธิภาพดำเนินงาน · SAO</div>
</div>
""", unsafe_allow_html=True)

# ── Main Tools ────────────────────────────────────────
st.markdown('<div class="sec"><div class="sec-title">เครื่องมือหลัก</div><div class="sec-line"></div></div>', unsafe_allow_html=True)
m1, m2, m3 = st.columns(3, gap="medium")

with m1:
    st.markdown("""
    <a class="hcard-link" href="Audit_Design_Assistant" target="_self">
      <div class="mcard">
        <div class="mcard-grid"></div>
        <div class="mcard-stripe"></div>
        <div class="mcard-icon">🏳️</div>
        <div class="mcard-title">Audit Design Assistant</div>
        <div class="mcard-desc">วิเคราะห์และสรุปเรื่อง 6W2H · Logic Model · ค้นหาข้อตรวจพบที่ผ่านมา · AI แนะนำประเด็น · ร่างรายงาน </div>
      </div>
    </a>""", unsafe_allow_html=True)

with m2:
    st.markdown("""
    <a class="hcard-link" href="Audit_Plan_Generator" target="_self">
      <div class="mcard">
        <div class="mcard-grid"></div>
        <div class="mcard-stripe"></div>
        <div class="mcard-icon">🔮</div>
        <div class="mcard-title">Audit Plan Generator</div>
        <div class="mcard-desc">ร่างแผนและแนวการตรวจสอบอัตโนมัติ AI สร้างเนื้อหา ส่งออก Word · HTML ได้ทันที</div>
      </div>
    </a>""", unsafe_allow_html=True)

with m3:
    st.markdown("""
    <a class="hcard-link" href="PA_Assistant_Chat" target="_self">
      <div class="mcard">
        <div class="mcard-grid"></div>
        <div class="mcard-stripe"></div>
        <div class="mcard-icon">🤖</div>
        <div class="mcard-title">PA Assistant Chat</div>
        <div class="mcard-desc">ถาม-ตอบผู้ช่วยอัจฉริยะ อ้างอิงคู่มือและผลการตรวจสอบ รองรับ PDF · CSV · TXT</div>
      </div>
    </a>""", unsafe_allow_html=True)

# ── Utility Tools ─────────────────────────────────────
st.markdown('<div class="sec" style="margin-top:24px;"><div class="sec-title">ยูทิลิตี้</div><div class="sec-line"></div></div>', unsafe_allow_html=True)
u1, u2, u3, u4, u5 = st.columns(5, gap="xxsmall")

with u1:
    st.markdown("""
    <a class="hcard-link" href="แปลงภาพเป็นข้อความ_(OCR)" target="_self">
      <div class="ucard">
        <div class="ucard-bar"></div>
        <div class="ucard-icon">📄</div>
        <div class="ucard-title">OCR แปลงภาพเป็นข้อความ</div>
        <div class="ucard-desc">ดึงข้อความจากภาพ · PDF ภาษาไทย–อังกฤษ แปลงเป็น Text · Doc</div>
      </div>
    </a>""", unsafe_allow_html=True)

with u2:
    st.markdown("""
    <a class="hcard-link" href="QR_Code_Generator" target="_self">
      <div class="ucard">
        <div class="ucard-bar"></div>
        <div class="ucard-icon">📱</div>
        <div class="ucard-title">QR Code Generator</div>
        <div class="ucard-desc">สร้าง QR Code พร้อมโลโก้หน่วยงาน ดาวน์โหลดได้ทันที</div>
      </div>
    </a>""", unsafe_allow_html=True)

with u3:
    st.markdown("""
    <a class="hcard-link" href="Audit_Dashboard" target="_self">
      <div class="ucard">
        <div class="ucard-bar"></div>
        <div class="ucard-icon">📊</div>
        <div class="ucard-title">Audit Dashboard</div>
        <div class="ucard-desc">Dashboard ตัวช่วยสรุปข้อมูลและนำเสนอข้อมูลด้วยภาพ</div>
      </div>
    </a>""", unsafe_allow_html=True)

with u4:
    st.markdown("""
    <a class="hcard-link" href="Analytics_Sandbox" target="_self">
      <div class="ucard">
        <div class="ucard-bar"></div>
        <div class="ucard-icon">🕵️</div>
        <div class="ucard-title">Data Analytics Sandbox</div>
        <div class="ucard-desc">Power BI Mode · YData Profiling · PyGWalker วิเคราะห์ข้อมูลเชิงลึก</div>
      </div>
    </a>""", unsafe_allow_html=True)

with u5:
    st.markdown("""
    <a class="hcard-link" href="GIS_Explorer" target="_self">
      <div class="ucard">
        <div class="ucard-bar"></div>
        <div class="ucard-icon">🗺️</div>
        <div class="ucard-title">GIS Explorer</div>
        <div class="ucard-desc">แสดงแผนที่/ข้อมูลเชิงพื้นที่ · Heatmap · Overlay · ตรวจสอบพื้นที่</div>
      </div>
    </a>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="infobox"><div style="font-size:14px;margin-top:1px;flex-shrink:0">⚠️</div><div>การใช้ฟีเจอร์ AI อาจผิดพลาดได้ โปรดตรวจสอบคำตอบอีกครั้ง ระบบไม่มีการจัดเก็บข้อมูลไว้</div></div>', unsafe_allow_html=True)

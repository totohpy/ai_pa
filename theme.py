# theme.py — PA Planning Studio v6.1
# เพิ่ม AI Provider selector ใน sidebar
# Fix: file uploader white bg using comprehensive selectors
# Fix: sidebar red + white text via CSS (config.toml secondaryBg = cream)

GOV_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Noto+Serif+Thai:wght@400;600;700&display=swap');
:root {
    --red:#7A2020; --red-dark:#621a1a;
    --cream:#FEFFD3; --green:#6D9E51; --green-lt:#BCD9A2; --green-pale:#e8f5e0;
    --bg:#f8f9ee; --bg-card:#ffffff; --border:#e3e4c4;
    --border-card:#d8d9b4; --text-h:#1a1a1a; --text-b:#404040; --text-mute:#7a7a7a;
}
html,body,[class*="css"],.stApp { font-family:'Sarabun',sans-serif !important; }
[data-testid="stAppViewContainer"]>.main { background-color:var(--bg) !important; }
.block-container { padding-top:1.6rem !important; padding-bottom:3rem !important; }

/* ═══ SIDEBAR ═══ */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div,
[data-testid="stSidebar"] > div > div > div {
    background-color:#7A2020 !important;
}
[data-testid="stSidebarNav"] a,
[data-testid="stSidebarNav"] a span,
[data-testid="stSidebarNav"] a p,
[data-testid="stSidebarNav"] li a {
    color:#ffffff !important;
    border-radius:4px !important;
    padding:3px 6px !important;
    margin-bottom:0px !important;
    font-size:14.5px !important;
    opacity:0.88;
    transition:background 0.05s !important;
    white-space:nowrap !important;
    overflow:hidden !important;
    text-overflow:ellipsis !important;
    display:block !important;
}
[data-testid="stSidebarNav"] a:hover { background:rgba(255,255,255,0.15) !important; opacity:1 !important; }
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background:rgba(255,255,255,0.22) !important;
    font-weight:700 !important;
    border:1px solid rgba(255,255,255,0.28) !important;
    opacity:1 !important;
}
/* ลด padding ของ sidebar โดยรวม */
[data-testid="stSidebarNav"] ul { padding:0 6px !important; margin:0 !important; }
[data-testid="stSidebarNav"] li { margin-bottom:2px !important; }

/* ── Sidebar: ทำให้ radio / text_input / expander ภายใน sidebar อ่านได้ ── */
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    color:#ffffff !important;
    font-size:13px !important;
}
[data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] p {
    color:#ffffff !important;
}
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stTextInput input {
    color:#1a1a1a !important;
    font-size:13px !important;
}
[data-testid="stSidebar"] details summary {
    color:rgba(255,255,255,0.75) !important;
    font-size:12px !important;
}
[data-testid="stSidebar"] details {
    background:rgba(255,255,255,0.08) !important;
    border-radius:8px !important;
    padding:4px 8px !important;
}
[data-testid="stSidebar"] details p,
[data-testid="stSidebar"] details code,
[data-testid="stSidebar"] details pre {
    color:rgba(255,255,255,0.80) !important;
    font-size:11px !important;
}
[data-testid="stSidebar"] code,
[data-testid="stSidebar"] pre {
    background:rgba(0,0,0,0.25) !important;
    color:#f0f0f0 !important;
    border-radius:4px !important;
}
/* radio dot color in sidebar */
[data-testid="stSidebar"] input[type="radio"] { accent-color:#ffffff !important; }

/* ═══ FILE UPLOADER — force WHITE ═══ */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploader"] > section,
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"] > div,
div[data-baseweb="file-uploader"],
div[data-baseweb="file-uploader"] > div,
div[class*="uploadedFile"],
div[class*="fileUploader"],
span[data-testid="stFileUploaderDropzone"] {
    background-color:#ffffff !important;
    background:#ffffff !important;
}

/* border ของ file uploader */
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploader"] > section {
    border:1.5px dashed #c8c9aa !important;
    border-radius:12px !important;
}
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploader"] > section:hover {
    border-color:var(--red) !important;
}

/* icon และ text ใน file uploader ให้ชัด */
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] small {
    color:var(--text-mute) !important;
}

/* ═══ TEXT AREA & INPUT — WHITE bg ═══ */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stNumberInput>div>div>input {
    background:#ffffff !important;
    border:1px solid var(--border-card) !important;
    border-radius:9px !important;
    color:var(--text-h) !important;
    font-family:'Sarabun',sans-serif !important;
    font-size:15px !important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {
    border-color:var(--red) !important;
    box-shadow:0 0 0 3px rgba(122,32,32,0.07) !important;
}
.stTextInput label,.stTextArea label,.stSelectbox label,
.stNumberInput label,.stSlider label,.stFileUploader label,
.stMultiSelect label,.stDateInput label {
    color:var(--text-mute) !important;
    font-size:12px !important;
    font-weight:700 !important;
    text-transform:uppercase;
    letter-spacing:0.5px;
}

/* ═══ BUTTONS ═══ */
.stButton>button { border-radius:9px !important; font-family:'Sarabun',sans-serif !important; font-weight:600 !important; font-size:14px !important; transition:all 0.18s !important; }
button[data-testid="baseButton-primary"] { background:var(--red) !important; color:#fff !important; border:none !important; }
button[data-testid="baseButton-primary"]:hover { background:var(--red-dark) !important; transform:translateY(-1px) !important; box-shadow:0 4px 16px rgba(122,32,32,0.28) !important; }
button[data-testid="baseButton-secondary"] { background:#fff !important; color:var(--text-h) !important; border:1px solid var(--border-card) !important; }
button[data-testid="baseButton-secondary"]:hover { border-color:var(--red) !important; color:var(--red) !important; }

/* ═══ TABS ═══ */
div[data-baseweb="tab-list"] { background:#fff !important; border:1px solid var(--border-card) !important; border-radius:12px !important; padding:5px !important; gap:3px !important; border-bottom:none !important; flex-wrap:wrap !important; margin-bottom:16px !important; }
button[data-baseweb="tab"] { background:transparent !important; border-radius:8px !important; color:var(--text-mute) !important; font-size:13px !important; font-weight:500 !important; padding:7px 14px !important; border:none !important; box-shadow:none !important; transition:all 0.16s !important; transform:none !important; font-family:'Sarabun',sans-serif !important; }
button[data-baseweb="tab"]:hover { background:var(--cream) !important; color:var(--text-h) !important; }
button[data-baseweb="tab"][aria-selected="true"] { background:var(--red) !important; color:#fff !important; font-weight:600 !important; }

/* ═══ DATAFRAME ═══ */
.stDataFrame,.stDataEditor { border-radius:12px !important; overflow:hidden !important; border:1px solid var(--border-card) !important; }
.stDataFrame thead th { background:rgba(254,255,211,0.85) !important; color:var(--red) !important; font-size:11.5px !important; font-weight:700 !important; text-transform:uppercase !important; }
.stDataFrame tbody td { color:var(--text-b) !important; font-size:14px !important; }

/* ═══ ALERTS ═══ */
div[data-testid="stInfo"]    { background:var(--cream) !important; border:1px solid #e0e098 !important; border-left:4px solid var(--red) !important; border-radius:10px !important; }
div[data-testid="stSuccess"] { background:var(--green-pale) !important; border:1px solid var(--green-lt) !important; border-left:4px solid var(--green) !important; border-radius:10px !important; }
div[data-testid="stWarning"] { background:#fff8e1 !important; border:1px solid #ffe082 !important; border-left:4px solid #f59e0b !important; border-radius:10px !important; }
div[data-testid="stError"]   { background:rgba(122,32,32,0.05) !important; border:1px solid rgba(122,32,32,0.2) !important; border-left:4px solid var(--red) !important; border-radius:10px !important; }

/* ═══ CONTAINER ═══ */
div[data-testid="stVerticalBlockBorderWrapper"]>div { background:var(--bg-card) !important; border:1px solid var(--border-card) !important; border-radius:14px !important; padding:18px !important; }

/* ═══ CHAT ═══ */
div[data-testid="stChatMessage"] { background:var(--bg-card) !important; border:1px solid var(--border) !important; border-radius:12px !important; margin-bottom:8px !important; }
.stChatInput>div { background:#ffffff !important; border:1px solid var(--border-card) !important; border-radius:12px !important; }
.stChatInput>div:focus-within { border-color:var(--red) !important; }

/* ═══ MISC ═══ */
h1 { font-size:24px !important; font-weight:700 !important; color:var(--text-h) !important; font-family:'Noto Serif Thai',serif !important; }
h2 { font-size:19px !important; font-weight:700 !important; color:var(--text-h) !important; font-family:'Noto Serif Thai',serif !important; }
h3 { font-size:16px !important; font-weight:600 !important; color:var(--text-h) !important; }
h4 { font-size:12px !important; font-weight:700 !important; color:var(--red) !important; text-transform:uppercase; letter-spacing:1px; border-bottom:none !important; }
.stSelectbox>div>div,.stMultiSelect>div>div { background:#ffffff !important; border:1px solid var(--border-card) !important; border-radius:9px !important; }
/* multiselect tags — พื้นขาว ตัวอักษรแดง อ่านง่าย */
[data-baseweb="tag"] {
    background-color: rgba(122,32,32,0.12) !important;
    border: 1px solid rgba(122,32,32,0.35) !important;
    border-radius: 6px !important;
}
[data-baseweb="tag"] span {
    color: #7A2020 !important;
    font-weight: 600 !important;
}
[data-baseweb="tag"] [role="presentation"] svg {
    fill: #7A2020 !important;
}
/* ── ปุ่ม << ซ่อน sidebar (ใน sidebar) ── */
[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] {
    background-color: rgba(255,255,255,0.2) !important;
    border: 1px solid rgba(255,255,255,0.45) !important;
    border-radius: 6px !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    fill: #ffffff !important;
    stroke: #ffffff !important;
}
/* ── ปุ่ม >> เปิด sidebar (นอก sidebar) — ต้องเห็นชัดบน main ── */
[data-testid="collapsedControl"] {
    background-color: #7A2020 !important;
    border-radius: 0 8px 8px 0 !important;
    opacity: 1 !important;
    visibility: visible !important;
    display: flex !important;
    box-shadow: 2px 0 8px rgba(0,0,0,0.2) !important;
}
[data-testid="collapsedControl"] button {
    background: transparent !important;
}
[data-testid="collapsedControl"] svg {
    fill: #ffffff !important;
    stroke: #ffffff !important;
}
.stSlider>div>div>div>div { background:var(--red) !important; }
.stDownloadButton>button { background:var(--green-pale) !important; color:#2d5a1a !important; border:1px solid var(--green-lt) !important; border-radius:9px !important; font-weight:600 !important; }
div[data-testid="stMetric"] { background:var(--bg-card) !important; border:1px solid var(--border-card) !important; border-radius:12px !important; padding:16px !important; }
div[data-testid="stMetricLabel"] { color:var(--text-mute) !important; font-size:12px !important; font-weight:700 !important; text-transform:uppercase; }
div[data-testid="stMetricValue"] { color:var(--text-h) !important; font-size:24px !important; }
hr { border-color:var(--border) !important; margin:20px 0 !important; }
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-thumb { background:rgba(122,32,32,0.2); border-radius:10px; }

/* ═══ SIDEBAR FOOTER CARD ═══ */
.sb-footer { padding:12px; border-top:1px solid rgba(255,255,255,0.18); margin-top:12px; }
.sb-footer-card { background:rgba(255,255,255,0.13); border:1px solid rgba(255,255,255,0.22); border-radius:10px; padding:10px 12px; display:flex; align-items:center; gap:10px; }
.sb-emblem { width:32px; height:32px; background:rgba(255,255,255,0.22); border-radius:8px; display:flex; align-items:center; justify-content:center; flex-shrink:0; font-size:17px; }
.sb-name { font-size:13px; font-weight:700; display:block; color:#ffffff !important; }
.sb-org  { font-size:11px; opacity:0.70; margin-top:1px; display:block; color:#ffffff !important; }

/* ── ซ่อน Streamlit branding / toolbar ── */
#MainMenu                        { visibility:hidden !important; display:none !important; }
[data-testid="stDecoration"]     { visibility:hidden !important; display:none !important; }
[data-testid="stDeployButton"]   { visibility:hidden !important; display:none !important; }
[data-testid="stStatusWidget"]   { visibility:hidden !important; display:none !important; }
[data-testid="stToolbarActions"] { visibility:hidden !important; display:none !important; }
[data-testid="baseButton-header"] { display:none !important; }
[data-testid="manage-app-button"] { display:none !important; }
a[href*="github.com"]            { display:none !important; }
button[title="Fork this app"]    { display:none !important; }
/* ไม่ซ่อน stHeader และ stToolbar ทั้งก้อน เพราะปุ่ม >> collapsedControl อยู่ในนั้น */
/* ซ่อนเฉพาะ deploy/status ใน stBottom */
[data-testid="stBottom"] [data-testid="stDeployButton"]   { display:none !important; }
[data-testid="stBottom"] [data-testid="stStatusWidget"]   { display:none !important; }
[data-testid="stBottom"] [data-testid="stToolbarActions"] { display:none !important; }
/* bottom-right floating buttons */
.viewerBadge_container__r5tak   { display:none !important; }
.viewerBadge_link__qRIco        { display:none !important; }
#stDecoration                   { display:none !important; }
div[class*="StatusWidget"]      { display:none !important; }
</style>
"""

# SIDEBAR_HTML เป็น HTML-only ส่วน (footer card)
# AI Provider selector ถูก render ด้วย render_provider_sidebar() จาก ai_provider.py
SIDEBAR_HTML = """
<div class="sb-footer">
  <div class="sb-footer-card">
    <div class="sb-emblem">🏛️</div>
    <div>
      <span class="sb-name">Audit Intelligence Team</span>
      <span class="sb-org">By PAO1 · สตง.</span>
    </div>
  </div>
</div>
"""


def apply_theme():
    import streamlit as st
    # ── Anti-flash: sidebar สีแดงทันที + fade-in content ──
    st.markdown("""
<style>
/* sidebar พื้นหลังแดงทันทีไม่มี flash */
[data-testid="stSidebar"],
[data-testid="stSidebar"]>div,
[data-testid="stSidebar"]>div>div,
[data-testid="stSidebar"]>div>div>div,
[data-testid="stSidebarNav"] {
    background-color:#7A2020 !important;
}
[data-testid="stAppViewContainer"] {
    background-color:#f8f9ee !important;
}
/* fade-in sidebar content ทั้งหมด */
[data-testid="stSidebar"] > div:first-child {
    animation: sidebarFadeIn 0.35s ease-in forwards;
}
@keyframes sidebarFadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
/* ซ่อน Streamlit loading splash shapes */
#loading-spinner, .stSpinner,
[data-testid="stSkeleton"],
div[class*="loading"], div[class*="splash"] {
    display: none !important;
}
/* ซ่อน geometric shapes ของ Streamlit loading screen */
.element-container svg,
[data-testid="stAppViewContainer"] > div:first-child > div:first-child > svg {
    display: none !important;
}
</style>""", unsafe_allow_html=True)
    st.markdown(GOV_CSS, unsafe_allow_html=True)
    # ── ซ่อน toolbar ด้วย components.html (ทำงานกับทุก user บน Streamlit Cloud) ──
    import streamlit.components.v1 as components
    components.html("""
<script>
(function() {
    const SELECTORS = [
        '[data-testid="stDeployButton"]',
        '[data-testid="stStatusWidget"]',
        '[data-testid="stToolbarActions"]',
        '[data-testid="manage-app-button"]',
        '.viewerBadge_container__r5tak',
        'button[title="Fork this app"]',
    ];
    function hideAll() {
        var parent = window.parent.document;
        SELECTORS.forEach(function(sel) {
            parent.querySelectorAll(sel).forEach(function(el) {
                el.style.setProperty('display','none','important');
            });
        });
    }
    hideAll();
    new MutationObserver(hideAll).observe(
        window.parent.document.body,
        {childList:true, subtree:true}
    );
    var n=0, t=setInterval(function(){ hideAll(); if(++n>=20) clearInterval(t); },300);
})();
</script>
""", height=0)

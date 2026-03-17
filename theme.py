# theme.py — PA Planning Studio v6.2
# Color update: Emerald Green scheme
# Primary: #00c9a7 | Light bg: #e6faf6 | Dark hover: #4d8076

GOV_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Noto+Serif+Thai:wght@400;600;700&display=swap');
:root {
    --primary:#00c9a7;
    --primary-dark:#4d8076;
    --primary-light:#c4fcef;
    --primary-pale:#e6faf6;
    --primary-hover:#00b396;
    --bg:#f0fdf9;
    --bg-card:#ffffff;
    --border:#b2ede2;
    --border-card:#c8f0e8;
    --text-h:#0d2b25;
    --text-b:#1e4a40;
    --text-mute:#4d8076;
    --cream:#e6faf6;
    --sidebar:#00b396;
    --sidebar-dark:#007a67;
    --green:#4d8076;
    --green-lt:#b2ede2;
    --green-pale:#e6faf6;
}
html,body,[class*="css"],.stApp { font-family:'Sarabun',sans-serif !important; }
[data-testid="stAppViewContainer"]>.main { background-color:var(--bg) !important; }
.block-container { padding-top:1.6rem !important; padding-bottom:3rem !important; }

/* ═══ SIDEBAR ═══ */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div,
[data-testid="stSidebar"] > div > div > div {
    background-color:var(--sidebar) !important;
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
[data-testid="stSidebarNav"] a:hover { background:rgba(255,255,255,0.18) !important; opacity:1 !important; }
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background:rgba(255,255,255,0.28) !important;
    font-weight:700 !important;
    border:1px solid rgba(255,255,255,0.38) !important;
    opacity:1 !important;
}
[data-testid="stSidebarNav"] ul { padding:0 6px !important; margin:0 !important; }
[data-testid="stSidebarNav"] li { margin-bottom:2px !important; }

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
    color:rgba(255,255,255,0.85) !important;
    font-size:12px !important;
}
[data-testid="stSidebar"] details {
    background:rgba(255,255,255,0.12) !important;
    border-radius:8px !important;
    padding:4px 8px !important;
}
[data-testid="stSidebar"] details p,
[data-testid="stSidebar"] details code,
[data-testid="stSidebar"] details pre {
    color:rgba(255,255,255,0.85) !important;
    font-size:11px !important;
}
[data-testid="stSidebar"] code,
[data-testid="stSidebar"] pre {
    background:rgba(0,0,0,0.22) !important;
    color:#f0f0f0 !important;
    border-radius:4px !important;
}
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
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploader"] > section {
    border:1.5px dashed var(--border-card) !important;
    border-radius:12px !important;
}
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploader"] > section:hover {
    border-color:var(--primary) !important;
}
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
    border-color:var(--primary) !important;
    box-shadow:0 0 0 3px rgba(0,201,167,0.12) !important;
}
.stTextInput label,.stTextArea label,.stSelectbox label,
.stNumberInput label,.stSlider label,.stFileUploader label,
.stMultiSelect label,.stDateInput label {
    background:#ffffff !important;
    color:var(--text-mute) !important;
    font-size:12px !important;
    font-weight:700 !important;
    text-transform:uppercase;
    letter-spacing:0.5px;
}

/* ═══ DATE INPUT ═══
   BaseWeb วาดขอบด้วย box-shadow ไม่ใช่ border
   ต้องใช้ box-shadow inset แทน border เพื่อให้ตรงกับช่องอื่น
═══════════════════════════════════════════════════════════ */
div[data-testid="stDateInput"] div[data-baseweb="base-input"] {
    background-color: #ffffff !important;
    border-radius: 9px !important;
    /* ใช้ box-shadow inset แทน border — BaseWeb จะ override border ปกติ */
    box-shadow: inset 0 0 0 1px #c8f0e8 !important;
    border: none !important;
}
div[data-testid="stDateInput"] div[data-baseweb="base-input"]:focus-within {
    box-shadow: inset 0 0 0 1px #00c9a7, 0 0 0 3px rgba(0,201,167,0.12) !important;
}
div[data-testid="stDateInput"] div[data-baseweb="base-input"] input {
    background-color: #ffffff !important;
    color: #0d2b25 !important;
    font-family: 'Sarabun', sans-serif !important;
    font-size: 15px !important;
}
div[data-testid="stDateInput"] svg {
    fill: var(--primary-dark) !important;
}

/* ═══ BUTTONS ═══ */
.stButton>button {
    border-radius:9px !important;
    font-family:'Sarabun',sans-serif !important;
    font-weight:600 !important;
    font-size:14px !important;
    transition:all 0.18s !important;
}
button[data-testid="baseButton-primary"] {
    background:var(--primary) !important;
    color:#0d2b25 !important;
    border:none !important;
    font-weight:700 !important;
}
button[data-testid="baseButton-primary"]:hover {
    background:var(--primary-dark) !important;
    color:#ffffff !important;
    transform:translateY(-1px) !important;
    box-shadow:0 4px 16px rgba(0,201,167,0.30) !important;
}
button[data-testid="baseButton-secondary"] {
    background:#fff !important;
    color:var(--text-h) !important;
    border:1px solid var(--border-card) !important;
}
button[data-testid="baseButton-secondary"]:hover {
    border-color:var(--primary) !important;
    color:var(--primary-dark) !important;
}

/* ═══ TABS ═══ */
div[data-baseweb="tab-list"] {
    background:#fff !important;
    border:1px solid var(--border-card) !important;
    border-radius:12px !important;
    padding:5px !important;
    gap:3px !important;
    border-bottom:none !important;
    flex-wrap:wrap !important;
    margin-bottom:16px !important;
}
button[data-baseweb="tab"] {
    background:transparent !important;
    border-radius:8px !important;
    color:var(--text-mute) !important;
    font-size:13px !important;
    font-weight:500 !important;
    padding:7px 14px !important;
    border:none !important;
    box-shadow:none !important;
    transition:all 0.16s !important;
    transform:none !important;
    font-family:'Sarabun',sans-serif !important;
}
button[data-baseweb="tab"]:hover {
    background:var(--primary-pale) !important;
    color:var(--text-h) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background:var(--primary) !important;
    color:#0d2b25 !important;
    font-weight:700 !important;
}

/* ═══ DATAFRAME ═══ */
.stDataFrame,.stDataEditor {
    border-radius:12px !important;
    overflow:hidden !important;
    border:1px solid var(--border-card) !important;
}
.stDataFrame thead th {
    background:var(--primary-pale) !important;
    color:var(--primary-dark) !important;
    font-size:11.5px !important;
    font-weight:700 !important;
    text-transform:uppercase !important;
}
.stDataFrame tbody td { color:var(--text-b) !important; font-size:14px !important; }

/* ═══ ALERTS ═══ */
div[data-testid="stInfo"] {
    background:var(--primary-pale) !important;
    border:1px solid var(--border) !important;
    border-left:4px solid var(--primary) !important;
    border-radius:10px !important;
    color:var(--text-b) !important;
}
div[data-testid="stInfo"] p, div[data-testid="stInfo"] span {
    color:var(--text-b) !important;
}
div[data-testid="stSuccess"] {
    background:#e6faf6 !important;
    border:1px solid var(--green-lt) !important;
    border-left:4px solid var(--primary) !important;
    border-radius:10px !important;
    color:var(--text-b) !important;
}
div[data-testid="stSuccess"] p, div[data-testid="stSuccess"] span {
    color:var(--text-b) !important;
}
div[data-testid="stWarning"] {
    background:#fff8e1 !important;
    border:1px solid #ffe082 !important;
    border-left:4px solid #f59e0b !important;
    border-radius:10px !important;
    color:#5a3e00 !important;
}
div[data-testid="stWarning"] p, div[data-testid="stWarning"] span {
    color:#5a3e00 !important;
}
div[data-testid="stError"] {
    background:rgba(0,201,167,0.06) !important;
    border:1px solid rgba(0,201,167,0.25) !important;
    border-left:4px solid var(--primary) !important;
    border-radius:10px !important;
    color:var(--text-b) !important;
}
div[data-testid="stError"] p, div[data-testid="stError"] span {
    color:var(--text-b) !important;
}

/* ═══ CONTAINER ═══ */
div[data-testid="stVerticalBlockBorderWrapper"]>div {
    background:var(--bg-card) !important;
    border:1px solid var(--border-card) !important;
    border-radius:14px !important;
    padding:18px !important;
}

/* ═══ CHAT ═══ */
div[data-testid="stChatMessage"] {
    background:var(--bg-card) !important;
    border:1px solid var(--border) !important;
    border-radius:12px !important;
    margin-bottom:8px !important;
}
.stChatInput>div {
    background:#ffffff !important;
    border:1px solid var(--border-card) !important;
    border-radius:12px !important;
}
.stChatInput>div:focus-within { border-color:var(--primary) !important; }

/* ═══ TYPOGRAPHY ═══ */
h1 {
    font-size:24px !important;
    font-weight:700 !important;
    color:var(--text-h) !important;
    font-family:'Noto Serif Thai',serif !important;
}
h2 {
    font-size:19px !important;
    font-weight:700 !important;
    color:var(--text-h) !important;
    font-family:'Noto Serif Thai',serif !important;
}
h3 { font-size:16px !important; font-weight:600 !important; color:var(--text-h) !important; }
h4 {
    font-size:12px !important;
    font-weight:700 !important;
    color:var(--primary-dark) !important;
    text-transform:uppercase;
    letter-spacing:1px;
    border-bottom:none !important;
}

/* ═══ SELECTBOX & MULTISELECT ═══ */
.stSelectbox>div>div,.stMultiSelect>div>div {
    background:#ffffff !important;
    border:1px solid var(--border-card) !important;
    border-radius:9px !important;
    color:var(--text-h) !important;
}
[data-baseweb="tag"] {
    background-color: rgba(0,201,167,0.15) !important;
    border: 1px solid rgba(0,201,167,0.40) !important;
    border-radius: 6px !important;
}
[data-baseweb="tag"] span {
    color: var(--primary-dark) !important;
    font-weight: 600 !important;
}
[data-baseweb="tag"] [role="presentation"] svg {
    fill: var(--primary-dark) !important;
}

/* ═══ SIDEBAR COLLAPSE BUTTON ═══ */
[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] {
    background-color: rgba(255,255,255,0.90) !important;
    border: 1px solid rgba(255,255,255,0.95) !important;
    border-radius: 6px !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    fill: var(--primary-dark) !important;
    stroke: var(--primary-dark) !important;
}
[data-testid="collapsedControl"] {
    background-color: var(--sidebar) !important;
    border-radius: 0 8px 8px 0 !important;
    opacity: 1 !important;
    visibility: visible !important;
    display: flex !important;
    box-shadow: 2px 0 8px rgba(0,0,0,0.15) !important;
}
[data-testid="collapsedControl"] button { background: transparent !important; }
[data-testid="collapsedControl"] svg {
    fill: #ffffff !important;
    stroke: #ffffff !important;
}

/* ═══ SLIDER ═══ */
.stSlider>div>div>div>div { background:var(--primary) !important; }

/* ═══ DOWNLOAD BUTTON ═══ */
.stDownloadButton>button {
    background:var(--primary-pale) !important;
    color:var(--primary-dark) !important;
    border:1px solid var(--border) !important;
    border-radius:9px !important;
    font-weight:600 !important;
}
.stDownloadButton>button:hover {
    background:var(--primary-light) !important;
    color:#0d2b25 !important;
}

/* ═══ METRICS ═══ */
div[data-testid="stMetric"] {
    background:var(--bg-card) !important;
    border:1px solid var(--border-card) !important;
    border-radius:12px !important;
    padding:16px !important;
}
div[data-testid="stMetricLabel"] {
    color:var(--text-mute) !important;
    font-size:12px !important;
    font-weight:700 !important;
    text-transform:uppercase;
}
div[data-testid="stMetricValue"] {
    color:var(--text-h) !important;
    font-size:24px !important;
}
div[data-testid="stMetricDelta"] span {
    color:var(--primary-dark) !important;
}

/* ═══ HR ═══ */
hr { border-color:var(--border) !important; margin:20px 0 !important; }

/* ═══ SCROLLBAR ═══ */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-thumb { background:rgba(0,201,167,0.25); border-radius:10px; }

/* ═══ SIDEBAR FOOTER CARD ═══ */
.sb-footer { padding:12px; border-top:1px solid rgba(255,255,255,0.22); margin-top:12px; }
.sb-footer-card { background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.28); border-radius:10px; padding:10px 12px; display:flex; align-items:center; gap:10px; }
.sb-emblem { width:32px; height:32px; background:rgba(255,255,255,0.25); border-radius:8px; display:flex; align-items:center; justify-content:center; flex-shrink:0; font-size:17px; }
.sb-name { font-size:13px; font-weight:700; display:block; color:#ffffff !important; }
.sb-org  { font-size:11px; opacity:0.75; margin-top:1px; display:block; color:#ffffff !important; }

/* ── ซ่อน Streamlit branding ── */
#MainMenu                        { visibility:hidden !important; display:none !important; }
[data-testid="stDecoration"]     { visibility:hidden !important; display:none !important; }
#stDecoration                    { display:none !important; }
.viewerBadge_container__r5tak   { display:none !important; }
.viewerBadge_link__qRIco        { display:none !important; }

/* ═══ RADIO & CHECKBOX ═══ */
input[type="radio"]:checked { accent-color: var(--primary) !important; }
input[type="checkbox"]:checked { accent-color: var(--primary) !important; }

/* ═══ EXPANDER ═══ */
div[data-testid="stExpander"] details {
    border:1px solid var(--border-card) !important;
    border-radius:10px !important;
    background:#ffffff !important;
}
div[data-testid="stExpander"] summary {
    color:var(--text-h) !important;
    font-weight:600 !important;
}
div[data-testid="stExpander"] summary:hover {
    color:var(--primary-dark) !important;
}

/* ═══ CAPTION & SMALL TEXT ═══ */
.stCaption, [data-testid="stCaptionContainer"] p {
    color:var(--text-mute) !important;
    font-size:12px !important;
}

/* ═══ PROGRESS BAR ═══ */
div[data-testid="stProgressBar"] > div > div {
    background:var(--primary) !important;
}
</style>
"""

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
    st.markdown("""
<style>
[data-testid="stSidebar"],
[data-testid="stSidebar"]>div,
[data-testid="stSidebar"]>div>div,
[data-testid="stSidebar"]>div>div>div,
[data-testid="stSidebarNav"] {
    background-color:#00b396 !important;
}
[data-testid="stAppViewContainer"] {
    background-color:#f0fdf9 !important;
}
[data-testid="stSidebar"] > div:first-child {
    animation: sidebarFadeIn 0.35s ease-in forwards;
}
@keyframes sidebarFadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
#loading-spinner, .stSpinner,
[data-testid="stSkeleton"],
div[class*="loading"], div[class*="splash"] {
    display: none !important;
}
</style>""", unsafe_allow_html=True)
    st.markdown(GOV_CSS, unsafe_allow_html=True)
    import streamlit.components.v1 as components
    components.html("""
<script>
(function() {
    const SELECTORS = [
        '.viewerBadge_container__r5tak',
        '.viewerBadge_link__qRIco',
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

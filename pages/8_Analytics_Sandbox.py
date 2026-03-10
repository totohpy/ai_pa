import streamlit as st
import pandas as pd
import os, sys
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import streamlit.components.v1 as components

import sys, os, pathlib
_here = pathlib.Path(__file__).resolve().parent
for _p in [_here.parent, _here, pathlib.Path(os.getcwd())]:
    if (_p / "theme.py").exists():
        if str(_p) not in sys.path: sys.path.insert(0, str(_p))
        break
try:
    from theme import apply_theme, SIDEBAR_HTML
    from ai_provider import render_provider_sidebar
except ImportError:
    def apply_theme(): pass
    SIDEBAR_HTML = "<p style='color:white'>AIT</p>"
    def render_provider_sidebar(): pass

# optional imports — ไม่พังถ้าไม่มี
try:
    from pygwalker.api.streamlit import StreamlitRenderer
    HAS_PYGWALKER = True
except ImportError:
    HAS_PYGWALKER = False

HAS_SWEETVIZ = False  # ไม่รองรับ numpy เวอร์ชันใหม่

try:
    from ydata_profiling import ProfileReport
    HAS_YDATA = True
except ImportError:
    HAS_YDATA = False

st.set_page_config(page_title="Super Analytics Sandbox", page_icon="🕵️", layout="wide")
apply_theme()

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    render_provider_sidebar()

# ── Thai Font Setup ───────────────────────────────────
def setup_thai_font():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir  = os.path.dirname(current_dir)
    font_paths  = [
        os.path.join(parent_dir, "Sarabun-Regular.ttf"),
        os.path.join(parent_dir, "Sarabun-Bold.ttf"),
        "Sarabun-Regular.ttf"
    ]
    found_path = next((p for p in font_paths if os.path.exists(p)), None)
    if found_path:
        fm.fontManager.addfont(found_path)
        prop = fm.FontProperties(fname=found_path)
        font_name = prop.get_name()
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        sns.set_theme(font=font_name)
        return font_name, True
    return None, False

thai_font_name, font_found = setup_thai_font()
if font_found:
    st.toast(f"✅ ฟอนต์: {thai_font_name}", icon="🇹🇭")

# ── UI ────────────────────────────────────────────────
st.title("🕵️ Super Analytics Sandbox")
st.markdown("เครื่องมือวิเคราะห์ข้อมูลครบวงจร")

with st.container(border=True):
    uploaded_file = st.file_uploader("📂 อัปโหลดไฟล์ Excel หรือ CSV", type=['xlsx','csv'])

@st.cache_data
def load_data(file):
    try:
        if file.name.endswith('.csv'): return pd.read_csv(file)
        else: return pd.read_excel(file)
    except: return None

@st.cache_resource
def get_pyg_renderer(dataframe):
    return StreamlitRenderer(dataframe, spec="./gw_config.json", spec_io_mode="RW")

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        st.success(f"✅ โหลดข้อมูลสำเร็จ: {df.shape[0]:,} รายการ, {df.shape[1]} คอลัมน์")

        tab_bi, tab_quick, tab_audit = st.tabs([
            "🎨 Power BI Mode",
            "📑 Quick Report",
            "🛠️ Audit Tools",
        ])

        # ── Power BI Mode (PyGWalker) ─────────────────
        with tab_bi:
            if HAS_PYGWALKER:
                renderer = get_pyg_renderer(df)
                renderer.explorer()
            else:
                st.warning("⚠️ PyGWalker ไม่พร้อมใช้งานบน Python เวอร์ชันนี้")
                st.info("ใช้แท็บ Quick Report หรือ Audit Tools แทนครับ")

        # ── Quick Report ──────────────────────────────
        with tab_quick:
            st.subheader("📑 Quick Report")

            if HAS_SWEETVIZ:
                if st.button("🚀 สร้างรายงาน Sweetviz", type="primary"):
                    with st.spinner("กำลังสร้างรายงาน..."):
                        report = sv.analyze(df)
                        report.show_html("sweetviz_report.html", open_browser=False, layout='vertical', scale=1.0)
                        with open("sweetviz_report.html", 'r', encoding='utf-8') as f:
                            components.html(f.read(), height=1000, scrolling=True)
            else:
                # ── Fallback: plotly ──────────────────
                import plotly.express as px
                num_cols = df.select_dtypes(include='number').columns.tolist()
                cat_cols = df.select_dtypes(include=['object','category']).columns.tolist()

                st.markdown("**สถิติเบื้องต้น**")
                st.dataframe(df.describe(), use_container_width=True)

                if num_cols:
                    st.markdown("**การกระจายของข้อมูล**")
                    col_sel = st.selectbox("เลือกคอลัมน์", num_cols, key="hist_col")
                    fig = px.histogram(df, x=col_sel, nbins=30,
                                       color_discrete_sequence=["#7A2020"],
                                       title=f"การกระจาย: {col_sel}")
                    fig.update_layout(plot_bgcolor="#f8f9ee", paper_bgcolor="#f8f9ee")
                    st.plotly_chart(fig, use_container_width=True)

                if len(num_cols) >= 2:
                    st.markdown("**Correlation Heatmap**")
                    corr = df[num_cols].corr().round(2)
                    fig_hm = px.imshow(corr, text_auto=True,
                                       color_continuous_scale="RdBu_r",
                                       title="Correlation Matrix", aspect="auto")
                    st.plotly_chart(fig_hm, use_container_width=True)

                if cat_cols:
                    st.markdown("**Value Counts**")
                    cat_sel = st.selectbox("เลือกคอลัมน์", cat_cols, key="vc_col")
                    vc = df[cat_sel].value_counts().reset_index()
                    vc.columns = [cat_sel, 'count']
                    fig_vc = px.bar(vc.head(20), x=cat_sel, y='count',
                                    color_discrete_sequence=["#7A2020"],
                                    title=f"Value Counts: {cat_sel}")
                    fig_vc.update_layout(plot_bgcolor="#f8f9ee", paper_bgcolor="#f8f9ee")
                    st.plotly_chart(fig_vc, use_container_width=True)

        # ── Audit Tools ───────────────────────────────
        with tab_audit:
            st.subheader("🛠️ Audit Tools")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**สุ่มตัวอย่าง**")
                sample_size = st.number_input("จำนวนสุ่ม", 1, len(df), min(5, len(df)))
                if st.button("สุ่มข้อมูล", type="primary"):
                    st.dataframe(df.sample(sample_size), use_container_width=True, hide_index=True)
            with c2:
                num_cols_audit = df.select_dtypes(include=['number']).columns.tolist()
                if num_cols_audit:
                    st.markdown("**Top 5 ตามคอลัมน์**")
                    col = st.selectbox("เรียงตาม", num_cols_audit)
                    if st.button("แสดง Top 5", type="secondary"):
                        st.dataframe(df.nlargest(5, col), use_container_width=True, hide_index=True)
                else:
                    st.info("ไม่พบคอลัมน์ตัวเลขในข้อมูล")
    else:
        st.error("ไม่สามารถอ่านไฟล์ได้ กรุณาตรวจสอบรูปแบบไฟล์")
else:
    st.info("👆 กรุณาอัปโหลดไฟล์ Excel หรือ CSV เพื่อเริ่มต้น")

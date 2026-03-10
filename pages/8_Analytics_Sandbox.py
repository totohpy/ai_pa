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

        tab_bi, tab_quick, tab_profile, tab_join, tab_groupby, tab_audit = st.tabs([
            "🎨 Power BI Mode",
            "📑 Quick Report",
            "🔬 Data Profiling",
            "🔗 Join ตาราง",
            "📊 Group by / Pivot",
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

            if HAS_YDATA:
                if st.button("🚀 สร้างรายงาน YData Profiling", type="primary"):
                    with st.spinner("กำลังสร้างรายงาน... (อาจใช้เวลาสักครู่)"):
                        try:
                            profile = ProfileReport(df, title="PA Data Report",
                                                    explorative=True, minimal=False)
                            profile.to_file("ydata_report.html")
                            with open("ydata_report.html", 'r', encoding='utf-8') as f:
                                components.html(f.read(), height=1000, scrolling=True)
                        except Exception as e:
                            st.error(f"YData error: {e}")
            elif HAS_SWEETVIZ:
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

        # ── Data Profiling (YData-style) ──────────────────
        with tab_profile:
            st.subheader("🔬 Data Profiling Report")
            st.caption("วิเคราะห์ข้อมูลเชิงลึกแบบ YData Profiling — ไม่ต้องติดตั้ง library เพิ่ม")

            import plotly.express as px
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots

            # ── Overview ──────────────────────────────────
            with st.container(border=True):
                st.markdown("#### 📋 Dataset Overview")
                n_rows, n_cols = df.shape
                n_dup   = df.duplicated().sum()
                n_miss  = df.isnull().sum().sum()
                miss_pct = n_miss / (n_rows * n_cols) * 100 if n_rows * n_cols > 0 else 0
                n_num   = len(df.select_dtypes(include='number').columns)
                n_cat   = len(df.select_dtypes(include=['object','category']).columns)

                c1,c2,c3,c4,c5,c6 = st.columns(6)
                c1.metric("แถวทั้งหมด",    f"{n_rows:,}")
                c2.metric("คอลัมน์",       f"{n_cols:,}")
                c3.metric("ตัวเลข",        f"{n_num}")
                c4.metric("ข้อความ",       f"{n_cat}")
                c5.metric("Duplicates",    f"{n_dup:,}")
                c6.metric("Missing %",     f"{miss_pct:.1f}%")

            # ── Missing Values Heatmap ─────────────────────
            missing = df.isnull().sum()
            missing = missing[missing > 0]
            if len(missing) > 0:
                with st.container(border=True):
                    st.markdown("#### ❗ Missing Values")
                    miss_df = pd.DataFrame({
                        "คอลัมน์": missing.index,
                        "จำนวน Missing": missing.values,
                        "% Missing": (missing.values / n_rows * 100).round(2)
                    }).sort_values("จำนวน Missing", ascending=False)
                    c1, c2 = st.columns([1,2])
                    with c1:
                        st.dataframe(miss_df, hide_index=True, use_container_width=True)
                    with c2:
                        fig_miss = px.bar(miss_df, x="คอลัมน์", y="% Missing",
                            title="% Missing per Column",
                            color="% Missing", color_continuous_scale="Reds")
                        fig_miss.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                        st.plotly_chart(fig_miss, use_container_width=True)
            else:
                st.success("✅ ไม่มี Missing Values!")

            # ── Column-by-Column Profile ───────────────────
            with st.container(border=True):
                st.markdown("#### 🔍 Column Profiles")
                col_sel = st.selectbox("เลือกคอลัมน์ที่ต้องการวิเคราะห์", df.columns.tolist(), key="profile_col")
                series = df[col_sel]
                dtype  = series.dtype

                pc1, pc2 = st.columns(2)
                with pc1:
                    st.markdown("**สถิติพื้นฐาน**")
                    stats = {
                        "Type":     str(dtype),
                        "Count":    f"{series.count():,}",
                        "Missing":  f"{series.isnull().sum():,} ({series.isnull().mean()*100:.1f}%)",
                        "Unique":   f"{series.nunique():,}",
                    }
                    if pd.api.types.is_numeric_dtype(series):
                        stats.update({
                            "Mean":   f"{series.mean():.4f}",
                            "Median": f"{series.median():.4f}",
                            "Std":    f"{series.std():.4f}",
                            "Min":    f"{series.min():.4f}",
                            "Max":    f"{series.max():.4f}",
                            "Skew":   f"{series.skew():.4f}",
                            "Kurt":   f"{series.kurtosis():.4f}",
                        })
                    else:
                        top = series.value_counts().head(1)
                        stats.update({
                            "Most Common": f"{top.index[0]} ({top.values[0]:,})" if len(top) > 0 else "-",
                        })
                    for k,v in stats.items():
                        st.markdown(f"- **{k}:** {v}")

                with pc2:
                    if pd.api.types.is_numeric_dtype(series):
                        fig_h = px.histogram(series.dropna(), nbins=30,
                            title=f"Distribution: {col_sel}",
                            color_discrete_sequence=["#7A2020"])
                        fig_h.update_layout(plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
                        st.plotly_chart(fig_h, use_container_width=True)
                    else:
                        vc = series.value_counts().head(15).reset_index()
                        vc.columns = [col_sel, "count"]
                        fig_b = px.bar(vc, x=col_sel, y="count",
                            title=f"Top Values: {col_sel}",
                            color_discrete_sequence=["#7A2020"])
                        fig_b.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                        st.plotly_chart(fig_b, use_container_width=True)

            # ── Correlation Matrix ─────────────────────────
            num_df = df.select_dtypes(include='number')
            if len(num_df.columns) >= 2:
                with st.container(border=True):
                    st.markdown("#### 🔗 Correlation Matrix")
                    corr = num_df.corr()
                    fig_corr = px.imshow(corr, text_auto=".2f",
                        color_continuous_scale="RdBu_r",
                        title="Correlation Heatmap", aspect="auto")
                    fig_corr.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                    st.plotly_chart(fig_corr, use_container_width=True)

            # ── Duplicate Rows ─────────────────────────────
            if n_dup > 0:
                with st.container(border=True):
                    st.markdown(f"#### ⚠️ Duplicate Rows ({n_dup:,} แถว)")
                    if st.checkbox("แสดงแถวที่ซ้ำ", key="show_dup"):
                        st.dataframe(df[df.duplicated(keep=False)].sort_values(df.columns[0].tolist()),
                            use_container_width=True, hide_index=False)

        # ── Join ตาราง ────────────────────────────────────
        with tab_join:
            st.subheader("🔗 Join 2 ตาราง")
            st.info("อัปโหลดไฟล์ที่ 2 เพื่อ Join กับตารางหลักที่อัปโหลดด้านบน")

            uploaded_file2 = st.file_uploader("📂 อัปโหลดตารางที่ 2", type=['xlsx','csv'], key="file2")

            @st.cache_data
            def load_data2(file):
                try:
                    if file.name.endswith('.csv'): return pd.read_csv(file)
                    else: return pd.read_excel(file)
                except: return None

            if uploaded_file2:
                df2 = load_data2(uploaded_file2)
                if df2 is not None:
                    st.success(f"✅ ตารางที่ 2: {df2.shape[0]:,} แถว × {df2.shape[1]} คอลัมน์")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        key1 = st.selectbox("🔑 Key จากตาราง 1", df.columns.tolist(), key="join_key1")
                    with col2:
                        key2 = st.selectbox("🔑 Key จากตาราง 2", df2.columns.tolist(), key="join_key2")
                    with col3:
                        join_type = st.selectbox("ประเภท Join", [
                            "inner — เฉพาะที่ตรงกัน",
                            "left — ทุกแถวตาราง 1",
                            "right — ทุกแถวตาราง 2",
                            "outer — ทั้งหมด",
                        ])
                        join_how = join_type.split(" — ")[0]

                    with st.expander("👀 ตัวอย่างข้อมูลทั้ง 2 ตาราง"):
                        c1, c2 = st.columns(2)
                        c1.markdown("**ตาราง 1**")
                        c1.dataframe(df.head(5), use_container_width=True, hide_index=True)
                        c2.markdown("**ตาราง 2**")
                        c2.dataframe(df2.head(5), use_container_width=True, hide_index=True)

                    if st.button("🔗 Join ตาราง", type="primary"):
                        try:
                            joined = pd.merge(df, df2, left_on=key1, right_on=key2, how=join_how)
                            st.session_state['joined_df'] = joined
                            st.success(f"✅ Join สำเร็จ! ได้ {joined.shape[0]:,} แถว × {joined.shape[1]} คอลัมน์")
                        except Exception as e:
                            st.error(f"Join ไม่ได้: {e}")

                    if 'joined_df' in st.session_state:
                        joined = st.session_state['joined_df']
                        st.dataframe(joined, use_container_width=True, hide_index=True)
                        st.download_button("⬇️ ดาวน์โหลดผลลัพธ์ CSV",
                            joined.to_csv(index=False, encoding='utf-8-sig'),
                            "joined_data.csv", "text/csv")
            else:
                st.warning("กรุณาอัปโหลดตารางที่ 2 ก่อนครับ")

        # ── Group by / Pivot ──────────────────────────────
        with tab_groupby:
            st.subheader("📊 Group by / Pivot Table")
            import plotly.express as px

            data_source = st.radio("ข้อมูลที่ใช้",
                ["ตารางหลัก", "ตารางที่ Join แล้ว (ถ้ามี)"], horizontal=True)
            work_df = st.session_state.get('joined_df', df) if data_source == "ตารางที่ Join แล้ว (ถ้ามี)" else df

            num_cols = work_df.select_dtypes(include='number').columns.tolist()
            cat_cols = work_df.select_dtypes(include=['object','category']).columns.tolist()

            st.markdown("#### Group by")
            with st.container(border=True):
                gc1, gc2, gc3 = st.columns(3)
                group_cols = gc1.multiselect("Group by คอลัมน์", cat_cols or work_df.columns.tolist(), key="grp_cols")
                agg_col    = gc2.selectbox("คำนวณคอลัมน์", num_cols or work_df.columns.tolist(), key="grp_val")
                agg_func   = gc3.selectbox("ฟังก์ชัน", ["sum","mean","count","max","min","median"], key="grp_func")
                if group_cols and agg_col:
                    grouped = work_df.groupby(group_cols)[agg_col].agg(agg_func).reset_index()
                    grouped.columns = group_cols + [f"{agg_func}({agg_col})"]
                    grouped = grouped.sort_values(grouped.columns[-1], ascending=False)
                    st.dataframe(grouped, use_container_width=True, hide_index=True)
                    if len(group_cols) == 1:
                        fig = px.bar(grouped.head(20), x=group_cols[0], y=grouped.columns[-1],
                            title=f"{agg_func}({agg_col}) แยกตาม {group_cols[0]}",
                            color_discrete_sequence=["#7A2020"])
                        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                        st.plotly_chart(fig, use_container_width=True)
                    st.download_button("⬇️ ดาวน์โหลด CSV",
                        grouped.to_csv(index=False, encoding='utf-8-sig'), "grouped.csv", "text/csv")
                else:
                    st.info("เลือก Group by คอลัมน์และคอลัมน์ที่ต้องการคำนวณ")

            st.markdown("#### Pivot Table")
            with st.container(border=True):
                pc1, pc2, pc3, pc4 = st.columns(4)
                pivot_idx  = pc1.selectbox("แถว (Index)", cat_cols or work_df.columns.tolist(), key="pvt_idx")
                pivot_col  = pc2.selectbox("คอลัมน์ (Columns)", ["(ไม่มี)"] + cat_cols, key="pvt_col")
                pivot_val  = pc3.selectbox("ค่า (Values)", num_cols or work_df.columns.tolist(), key="pvt_val")
                pivot_func = pc4.selectbox("ฟังก์ชัน", ["sum","mean","count","max","min"], key="pvt_func")
                if st.button("สร้าง Pivot Table", type="primary"):
                    try:
                        cols_arg = None if pivot_col == "(ไม่มี)" else pivot_col
                        pivot = pd.pivot_table(work_df, index=pivot_idx,
                            columns=cols_arg, values=pivot_val,
                            aggfunc=pivot_func, fill_value=0)
                        st.dataframe(pivot, use_container_width=True)
                        st.download_button("⬇️ ดาวน์โหลด Pivot CSV",
                            pivot.to_csv(encoding='utf-8-sig'), "pivot.csv", "text/csv")
                    except Exception as e:
                        st.error(f"สร้าง Pivot ไม่ได้: {e}")

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

import streamlit as st
import streamlit.components.v1 as components
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from theme import apply_theme, SIDEBAR_HTML

st.set_page_config(layout="wide", page_title="Audit Dashboard")
apply_theme()

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)

st.title("📊 Environmental Audit Dashboard")
st.markdown("Dashboard สรุปสภาพปัญหาด้านสิ่งแวดล้อมในพื้นที่และการวางแผนตรวจสอบสิ่งแวดล้อม")

with st.container(border=True):
    iframe_code = """
    <iframe title="Envi_Audit_SAO2026"
    width="100%" height="612"
    src="https://app.powerbi.com/view?r=eyJrIjoiMzBmODQ2MTgtMGYwMy00NTc3LWI4ZTAtOWE1NzY3MjRkMGMwIiwidCI6ImI3NWFiN2IzLTU4YmEtNGZkNy1iYTU1LTMyNmY0ZWRmYzllOSIsImMiOjEwfQ%3D%3D"
    frameborder="0" allowFullScreen="true"></iframe>
    """
    components.html(iframe_code, height=620)

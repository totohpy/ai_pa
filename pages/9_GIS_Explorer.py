# -*- coding: utf-8 -*-
# 9_GIS_Explorer.py — PA Planning Studio
# GIS: basemap, shapefile, GeoJSON, CSV lat/lon, choropleth, heatmap, geoprocessing

import streamlit as st
import pandas as pd
import json, os, sys, pathlib, tempfile, zipfile

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
    SIDEBAR_HTML = ""
    def render_provider_sidebar(): pass

st.set_page_config(page_title="GIS Explorer", page_icon="🗺️", layout="wide")
apply_theme()

# ── CSS: แก้สี input/selectbox/multiselect/number_input ให้อ่านง่าย ─────────
st.markdown("""
<style>
/* ── number_input, text_input ── */
input[type="number"], input[type="text"], input[type="email"], input[type="password"] {
    background-color: #ffffff !important;
    color: #111111 !important;
    border: 1px solid #d0d0d0 !important;
    border-radius: 6px !important;
}
div[data-baseweb="input"], div[data-baseweb="base-input"] {
    background-color: #ffffff !important;
    border-radius: 6px !important;
}
div[data-baseweb="input"] > div,
div[data-baseweb="base-input"] > div {
    background-color: #ffffff !important;
}
/* ── textarea ── */
textarea {
    background-color: #ffffff !important;
    color: #111111 !important;
    border: 1px solid #d0d0d0 !important;
}
/* ── selectbox ── */
div[data-baseweb="select"] > div:first-child {
    background-color: #ffffff !important;
    color: #111111 !important;
    border: 1px solid #d0d0d0 !important;
    border-radius: 6px !important;
}
div[data-baseweb="select"] span,
div[data-baseweb="select"] div[class*="ValueContainer"] {
    color: #111111 !important;
}
div[data-baseweb="select"] svg { fill: #444444 !important; }
/* ── multiselect tags ── */
div[data-baseweb="tag"] {
    background-color: #eef2ff !important;
    color: #1a1a1a !important;
    border: 1px solid #b0bbf0 !important;
}
div[data-baseweb="tag"] span { color: #1a1a1a !important; }
/* ── dropdown list ── */
ul[data-baseweb="menu"] { background-color: #ffffff !important; }
li[role="option"] { background-color: #ffffff !important; color: #111111 !important; }
li[role="option"]:hover { background-color: #f0f4ff !important; }
li[aria-selected="true"] { background-color: #e8edff !important; }
/* ── file uploader ── */
div[data-testid="stFileUploaderDropzone"] {
    background-color: #f9f9fb !important;
    border: 1.5px dashed #aaaaaa !important;
    border-radius: 8px !important;
}
/* ── color picker label ── */
input[type="color"] {
    border: 1px solid #cccccc !important;
    border-radius: 4px !important;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    render_provider_sidebar()

# ── Optional imports ──────────────────────────────────────────────────────────
try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    import geopandas as gpd
    from shapely.geometry import Point
    HAS_GEO = True
except ImportError:
    HAS_GEO = False

try:
    import pydeck as pdk
    HAS_PYDECK = True
except ImportError:
    HAS_PYDECK = False

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🗺️ GIS Explorer")
st.markdown("วิเคราะห์และแสดงผลข้อมูลเชิงพื้นที่ — Shapefile · GeoJSON · CSV Lat/Lon · Heatmap · Choropleth")

# ── Dependency check ──────────────────────────────────────────────────────────
if not HAS_FOLIUM or not HAS_GEO:
    st.error("❌ กรุณาเพิ่ม library ใน requirements.txt")
    missing = []
    if not HAS_FOLIUM: missing += ["folium", "streamlit-folium"]
    if not HAS_GEO:    missing += ["geopandas", "shapely"]
    st.code("\n".join(missing))
    st.stop()

# ── Tabs ──────────────────────────────────────────────────────────────────────
# ── Tab definitions ──────────────────────────────────────────────────────────
tab_map, tab_heatmap, tab_spatial, tab_arcgis = st.tabs([
    "🗺️ แผนที่/ข้อมูลเชิงพื้นที่",
    "🌡️ Heatmap",
    "🔍 ตรวจสอบ/ประมวลผลข้อมูล",
    "🏛️ ArcGIS Viewer",
])
with tab_map:
    CENTER_LAT, CENTER_LON, ZOOM = 13.7563, 100.5018, 6
    from folium import plugins as fp

    _L = "https://ms.longdo.com/mapproxy/service"

    # Basemap definitions — ทั้งหมดจะเป็น TileLayer ใน folium (ไม่ใช่ Streamlit widget)
    BASEMAP_LAYERS = [
        ("🗺️ OpenStreetMap",          "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",          "© OpenStreetMap contributors", False),
        ("🛰️ OpenStreetMap Satellite", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", "© Esri", False),
        ("🌍 Esri World Street Map",   "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", "© Esri", False),
        ("🛰️ Esri Satellite",          "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", "© Esri", False),
        ("🚗 Google Roads",            "https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}",         "© Google", False),
        ("🛰️ Google Satellite",        "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",         "© Google", False),
        ("🛰️ Google Hybrid",           "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",         "© Google", False),
        ("🚦 Google Traffic",          "https://mt1.google.com/vt/lyrs=m@221097413,traffic&x={x}&y={y}&z={z}", "© Google", False),
    ]

    # WMS/Overlay catalog — ทั้งหมดเป็น overlay TileLayer ใน folium
    WMS_LAYERS = [
        # (name, type, url, layers_or_none, attr, fmt, transparent)
        ("🗺️ Longdo Political (ไทย)",          "wms",  _L, "longdo_political",       "© Longdo",           "image/png", True),
        ("🛰️ Longdo Bluemarble Terrain",         "wms",  _L, "bluemarble_terrain",     "© Longdo",           "image/png", True),
        ("🛰️ Thaichote (GISTDA 2560-2562)",      "wms",  _L, "thaichote",             "© GISTDA",           "image/png", True),
        ("🛰️ LDD Orthophoto (2547-2550)",        "wms",  _L, "ldd_ortho",             "© กรมพัฒนาที่ดิน",  "image/png", True),
        ("🏙️ ผังเมือง ทั่วประเทศ (DPT+เมือง)",  "wms",  _L, "cityplan_thailand",     "© กรมโยธา",          "image/png", True),
        ("🏙️ ผังเมือง DPT",                     "wms",  _L, "cityplan_dpt",          "© กรมโยธา",          "image/png", True),
        ("🏙️ ผังเมือง ระดับจังหวัด",             "wms",  _L, "cityplan_provinces",    "© Longdo",           "image/png", True),
        ("🏙️ ผังเมือง ระดับเมือง",              "wms",  _L, "cityplan_cities",       "© Longdo",           "image/png", True),
        ("🏛️ กรมที่ดิน (DOL)",                  "wms",  _L, "dol",                   "© กรมที่ดิน",         "image/png", True),
        ("🏛️ กรมที่ดิน HD",                     "wms",  _L, "dol_hd",                "© กรมที่ดิน",         "image/png", True),
        ("🏛️ กรมทางหลวง (DOH)",                 "wms",  _L, "doh_section_km",        "© กรมทางหลวง",        "image/png", True),
        ("🏛️ การใช้ที่ดิน LDD (2561-2563)",     "wms",  _L, "ldd_landuse_2561_2563", "© กรมพัฒนาที่ดิน",  "image/png", True),
        ("👥 ประชากรไทย 2020",                  "wms",  _L, "thailand_population",   "© Longdo",           "image/png", True),
        ("👥 FB Population (รวม)",              "wms",  _L, "fb_population_2020",    "© Facebook/Longdo",  "image/png", True),
        ("👥 FB Population (ผู้สูงอายุ)",        "wms",  _L, "fb_population_elderly", "© Facebook/Longdo", "image/png", True),
        ("👥 FB Population (เด็ก)",             "wms",  _L, "fb_population_children","© Facebook/Longdo",  "image/png", True),
        ("🚗 อุบัติเหตุ 2564 (3 หน่วยงาน)",     "wms",  _L, "accident_3Bura_2564",   "© DGA/Longdo",       "image/png", True),
        ("🚗 อุบัติเหตุ 2563",                  "wms",  _L, "accident_3Bura_2563",   "© DGA/Longdo",       "image/png", True),
        ("🚗 อุบัติเหตุ 2562",                  "wms",  _L, "accident_3Bura_2562",   "© DGA/Longdo",       "image/png", True),
        ("🚗 อุบัติเหตุ iTIC 2564",             "wms",  _L, "accident_itic_2564",    "© iTIC/Longdo",      "image/png", True),
        ("🌊 น้ำท่วม GISTDA (realtime)",        "wms",  _L, "gistda_flood_update",   "© GISTDA/Longdo",    "image/png", True),
        ("⛰️ ความชัน เกาะสมุย",                 "wms",  _L, "samui_slope",           "© Longdo",           "image/png", True),
        ("🌳 กรมป่าไม้ (RFD Basemap)",           "wms",  "https://gis.forest.go.th/arcgis/services/RFD_BASEMAP/MapServer/WMSServer", "0", "© กรมป่าไม้", "image/png", True),
        ("🌍 NASA GIBS MODIS Terra",             "tile", "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2024-01-01/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg", None, "© NASA GIBS", None, None),
        ("🌍 NASA VIIRS Night Lights",           "tile", "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_DayNightBand_ENCC/default/2024-01-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.png", None, "© NASA GIBS", None, None),
        ("🌍 OpenTopoMap",                      "tile", "https://tile.opentopomap.org/{z}/{x}/{y}.png", None, "© OpenTopoMap", None, None),
        ("🌍 Esri World Shaded Relief",          "tile", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}", None, "© Esri", None, None),
    ]

    # ── side controls (ไม่มี basemap/WMS widget แล้ว — อยู่ใน folium LayerControl) ──
    col_ctrl, col_map = st.columns([1, 3], gap="small")

    with col_ctrl:
        st.caption("💡 สลับ Basemap/Layer ได้จาก **🗂 ไอคอนมุมขวาบนแผนที่** โดยตรง")

        # ── นำเข้าข้อมูล ────────────────────────────────────────────────────
        with st.expander("📂 **นำเข้าข้อมูล**", expanded=False):
            file_type = st.radio("ประเภทไฟล์:",
                ["GeoJSON", "Shapefile (.zip)", "CSV (Lat/Lon)"],
                horizontal=False, key="import_file_type")

            if file_type == "GeoJSON":
                geo_file = st.file_uploader("อัปโหลด GeoJSON", type=["geojson","json"], key="geojson_up")
                if geo_file:
                    try:
                        gdf_new = gpd.read_file(geo_file)
                        st.session_state.gdf_loaded = gdf_new
                        st.session_state.csv_gdf    = None
                        st.success(f"✅ {len(gdf_new):,} features")
                        st.dataframe(gdf_new[[c for c in gdf_new.columns if c!="geometry"]].head(3), hide_index=True)
                    except Exception as e:
                        st.error(str(e))

            elif file_type == "Shapefile (.zip)":
                st.caption("💡 zip ไฟล์ .shp .shx .dbf .prj รวมกัน")
                shp_file = st.file_uploader("Shapefile (.zip)", type=["zip"], key="shp_up")
                if shp_file:
                    try:
                        with tempfile.TemporaryDirectory() as tmp:
                            zp = os.path.join(tmp,"d.zip")
                            with open(zp,"wb") as f: f.write(shp_file.read())
                            with zipfile.ZipFile(zp) as z: z.extractall(tmp)
                            shps = [f for f in os.listdir(tmp) if f.endswith(".shp")]
                            if not shps: st.error("ไม่พบ .shp")
                            else:
                                gdf_new = gpd.read_file(os.path.join(tmp,shps[0]))
                                st.session_state.gdf_loaded = gdf_new
                                st.session_state.csv_gdf    = None
                                st.success(f"✅ {len(gdf_new):,} features")
                                st.dataframe(gdf_new[[c for c in gdf_new.columns if c!="geometry"]].head(3), hide_index=True)
                    except Exception as e:
                        st.error(str(e))

            else:  # CSV
                csv_file = st.file_uploader("CSV (Lat/Lon)", type=["csv"], key="csv_geo")
                if csv_file:
                    df_csv = pd.read_csv(csv_file)
                    st.dataframe(df_csv.head(3), hide_index=True)
                    lat_col = st.selectbox("Latitude col",  df_csv.columns.tolist(), key="lat_col_main")
                    lon_col = st.selectbox("Longitude col", df_csv.columns.tolist(), key="lon_col_main")
                    if st.button("📍 โหลด", type="primary", key="load_csv_main"):
                        try:
                            df_c = df_csv.copy()
                            df_c["_lat"] = pd.to_numeric(df_c[lat_col], errors="coerce")
                            df_c["_lon"] = pd.to_numeric(df_c[lon_col], errors="coerce")
                            df_c = df_c.dropna(subset=["_lat","_lon"])
                            gdf_csv = gpd.GeoDataFrame(
                                df_c, geometry=gpd.points_from_xy(df_c["_lon"],df_c["_lat"]), crs="EPSG:4326")
                            st.session_state.csv_gdf    = gdf_csv
                            st.session_state.gdf_loaded = None
                            st.success(f"✅ {len(gdf_csv):,} จุด")
                        except Exception as e:
                            st.error(str(e))

            has_vector = "gdf_loaded" in st.session_state and st.session_state.gdf_loaded is not None
            has_csv    = "csv_gdf"    in st.session_state and st.session_state.csv_gdf    is not None
            if has_vector:
                r1,r2 = st.columns([3,1])
                r1.info(f"📂 **{len(st.session_state.gdf_loaded):,}** features")
                if r2.button("🗑️",key="del_layer",help="ลบ"): st.session_state.gdf_loaded=None; st.rerun()
            if has_csv:
                r1,r2 = st.columns([3,1])
                r1.info(f"📍 **{len(st.session_state.csv_gdf):,}** จุด")
                if r2.button("🗑️",key="del_csv",help="ลบ"): st.session_state.csv_gdf=None; st.rerun()

        # ── ค้นหาตำแหน่ง ────────────────────────────────────────────────────
        with st.expander("🔍 **ค้นหาตำแหน่ง**", expanded=False):
            gc_mode = st.radio("โหมด:", ["🔤 ชื่อสถานที่","📌 ระบุพิกัด"],
                               horizontal=True, key="gc_mode")
            if gc_mode == "🔤 ชื่อสถานที่":
                search_q = st.text_input("ชื่อสถานที่", key="geocode_q",
                                          placeholder="กรุงเทพ, Chiang Mai …")
                if st.button("🔍 ค้นหา", key="geocode_btn") and search_q:
                    try:
                        import requests as _req
                        _r = _req.get(
                            "https://nominatim.openstreetmap.org/search",
                            params={"q":search_q,"format":"json","limit":5,"accept-language":"th,en"},
                            headers={"User-Agent":"PA-GIS/1.0"}, timeout=10)
                        _geo = _r.json()
                        if _geo: st.session_state["geocode_results"] = _geo
                        else: st.warning("ไม่พบตำแหน่ง")
                    except Exception as e:
                        st.error(str(e))
                if "geocode_results" in st.session_state:
                    _res  = st.session_state["geocode_results"]
                    _labs = [r.get("display_name","")[:70] for r in _res]
                    _sel  = st.selectbox("เลือก:", _labs, key="geocode_pick")
                    _sr   = _res[_labs.index(_sel)]
                    CENTER_LAT = float(_sr["lat"]); CENTER_LON = float(_sr["lon"]); ZOOM = 13
                    st.caption(f"📍 {_sr.get('display_name','')[:80]}")
            else:
                coord_lat = st.number_input("Latitude",  value=13.7563,  format="%.6f", key="coord_lat")
                coord_lon = st.number_input("Longitude", value=100.5018, format="%.6f", key="coord_lon")
                if st.button("📌 ปักหมุด", type="primary", key="goto_coord"):
                    st.session_state["coord_target"] = (coord_lat, coord_lon)
                if "coord_target" in st.session_state:
                    _t = st.session_state["coord_target"]
                    CENTER_LAT, CENTER_LON, ZOOM = _t[0], _t[1], 13
                    st.success(f"📌 {_t[0]:.5f}, {_t[1]:.5f}")

        # ── ตัวเลือก ─────────────────────────────────────────────────────────
        with st.expander("⚙️ **ตัวเลือก**", expanded=False):
            opt_cluster  = st.toggle("🔵 Cluster จุด CSV",     value=True,  key="opt_cluster")
            opt_minimap  = st.toggle("🗺️ Mini Map",             value=False, key="opt_minimap")
            opt_measure  = st.toggle("📐 Measure tool",         value=False, key="opt_measure")
            opt_fullattr = st.toggle("📋 Popup เต็ม attribute", value=True,  key="opt_fullattr")
            opt_pin      = st.toggle("📍 โหมดปักหมุด (คลิกแผนที่)",   value=False, key="opt_pin")

        # ── รายการหมุด ───────────────────────────────────────────────────────
        if "pin_list" not in st.session_state:
            st.session_state["pin_list"] = []
        if opt_pin:
            if st.session_state["pin_list"]:
                with st.expander(f"📍 หมุดที่ปัก ({len(st.session_state['pin_list'])})", expanded=True):
                    st.caption("💡 ลาก marker บนแผนที่เพื่อย้าย แล้วคลิก 💾 อัปเดต")
                    for _i, (_plat, _plon, _plbl) in enumerate(st.session_state["pin_list"]):
                        _pa, _pb, _pc = st.columns([3, 1, 1])
                        _new_lbl = _pa.text_input("ชื่อ", value=_plbl, key=f"plbl_{_i}", label_visibility="collapsed")
                        if _new_lbl != _plbl:
                            st.session_state["pin_list"][_i] = (_plat, _plon, _new_lbl)
                            st.rerun()
                        _pa.caption(f"{_plat:.5f}, {_plon:.5f}")
                        if _pb.button("🗑️", key=f"dp{_i}", help="ลบหมุดนี้"):
                            st.session_state["pin_list"].pop(_i); st.rerun()
                    if st.button("🗑️ ลบทั้งหมด", key="clrpins"):
                        st.session_state["pin_list"] = []; st.rerun()
            else:
                st.info("👆 คลิกบนแผนที่เพื่อปักหมุด")

        # ── WMS GetFeatureInfo (ย้ายมาจาก tab_spatial) ──────────────────────
        with st.expander("🔍 **WMS GetFeatureInfo**", expanded=False):
            st.caption("คลิกบนแผนที่หลักด้านขวา แล้วกด Query → ถาม WMS server ณ จุดนั้น")
            _GFI_LAYERS = {
                "🏙️ ผังเมือง DPT":        {"url":"https://ms.longdo.com/mapproxy/service","layers":"cityplan_dpt"},
                "🏙️ ผังเมือง ทั่วประเทศ":  {"url":"https://ms.longdo.com/mapproxy/service","layers":"cityplan_thailand"},
                "🏛️ กรมที่ดิน (DOL)":     {"url":"https://ms.longdo.com/mapproxy/service","layers":"dol"},
                "🏛️ การใช้ที่ดิน LDD":    {"url":"https://ms.longdo.com/mapproxy/service","layers":"ldd_landuse_2561_2563"},
                "🚗 อุบัติเหตุ 2564":     {"url":"https://ms.longdo.com/mapproxy/service","layers":"accident_3Bura_2564"},
                "🌳 กรมป่าไม้ (RFD)":     {"url":"https://gis.forest.go.th/arcgis/services/RFD_BASEMAP/MapServer/WMSServer","layers":"0"},
                "🔧 กำหนด URL เอง":        {"url":"","layers":""},
            }
            _gfi_sel = st.selectbox("WMS Layer สำหรับ Query", list(_GFI_LAYERS.keys()), key="gfi_layer_sel")
            if _gfi_sel == "🔧 กำหนด URL เอง":
                _gc1,_gc2 = st.columns(2)
                _gfi_url    = _gc1.text_input("WMS URL",    key="gfi_url_custom")
                _gfi_layers = _gc2.text_input("Layer name", key="gfi_layers_custom")
            else:
                _gfi_url    = _GFI_LAYERS[_gfi_sel]["url"]
                _gfi_layers = _GFI_LAYERS[_gfi_sel]["layers"]
            _gfi_fmt = st.selectbox("Response Format",
                ["text/plain","text/html","application/json","text/xml"], key="gfi_fmt")
            st.caption("📍 คลิกบนแผนที่ด้านขวา → พิกัดจะถูกใช้อัตโนมัติ")
            if "gfi_clat" in st.session_state:
                _glat = st.session_state["gfi_clat"]; _glon = st.session_state["gfi_clon"]
                st.info(f"พิกัดล่าสุด: {_glat:.6f}, {_glon:.6f}")
                if st.button("🔍 Query WMS ณ จุดนี้", type="primary", key="run_gfi_main"):
                    if not _gfi_url or not _gfi_layers:
                        st.warning("กรุณาเลือก WMS layer ก่อน")
                    else:
                        try:
                            import requests as _req2
                            _d = 0.001
                            _p = {
                                "SERVICE":"WMS","VERSION":"1.3.0","REQUEST":"GetFeatureInfo",
                                "LAYERS":_gfi_layers,"QUERY_LAYERS":_gfi_layers,"STYLES":"",
                                "CRS":"EPSG:4326",
                                "BBOX":f"{_glat-_d},{_glon-_d},{_glat+_d},{_glon+_d}",
                                "WIDTH":"101","HEIGHT":"101","I":"50","J":"50",
                                "INFO_FORMAT":_gfi_fmt,"FEATURE_COUNT":"10",
                            }
                            _resp = _req2.get(_gfi_url, params=_p, timeout=15)
                            _resp.raise_for_status()
                            st.session_state["gfi_result"] = {
                                "content":_resp.text.strip(),"fmt":_gfi_fmt,
                                "status":_resp.status_code,"url":str(_resp.url),
                            }
                            st.rerun()
                        except Exception as _e:
                            st.error(f"GFI error: {_e}")
            else:
                st.info("👆 คลิกบนแผนที่ก่อน เพื่อเลือกตำแหน่ง")

            if "gfi_result" in st.session_state:
                _gr = st.session_state["gfi_result"]
                _gc = _gr["content"]; _gf = _gr["fmt"]
                st.markdown(f"**📡 Response** · HTTP {_gr['status']}")
                if not _gc or "no features" in _gc.lower():
                    st.info("ℹ️ ไม่พบข้อมูล")
                elif "text/plain" in _gf: st.code(_gc, language="text")
                elif "application/json" in _gf:
                    try:
                        import json as _json; _gj = _json.loads(_gc)
                        _feats = _gj.get("features",[])
                        if _feats:
                            st.success(f"✅ {len(_feats)} feature(s)")
                            for _fi,_ff in enumerate(_feats):
                                with st.expander(f"Feature {_fi+1}"): st.json(_ff.get("properties",{}))
                        else: st.json(_gj)
                    except: st.code(_gc, language="json")
                elif "html" in _gf: st.components.v1.html(_gc, height=250, scrolling=True)
                else: st.code(_gc, language="xml")

    # ══════════════════════════════════════════════════════════════════════════
    # Build Folium Map — Basemap + WMS ทั้งหมดอยู่ใน LayerControl ของ folium
    # การเปลี่ยน layer = browser-side เท่านั้น ไม่มี Python re-run
    # ══════════════════════════════════════════════════════════════════════════
    with col_map:
        # Resolve center
        if "coord_target" in st.session_state:
            _t = st.session_state["coord_target"]
            CENTER_LAT, CENTER_LON, ZOOM = _t[0], _t[1], 13
        if "geocode_results" in st.session_state:
            _r0 = st.session_state["geocode_results"]
            if _r0: CENTER_LAT=float(_r0[0]["lat"]); CENTER_LON=float(_r0[0]["lon"]); ZOOM=13

        # สร้างแผนที่ด้วย OpenStreetMap เป็น default (ไม่มี tiles เพื่อเพิ่มเอง)
        m = folium.Map(
            location=[CENTER_LAT, CENTER_LON], zoom_start=ZOOM,
            tiles=None,  # จะเพิ่ม basemap เองทั้งหมดด้านล่าง
            control_scale=True,
        )

        # ── เพิ่ม Basemap ทั้ง 8 เป็น TileLayer (base=True) ──────────────────
        for _i, (_name, _url, _attr, _) in enumerate(BASEMAP_LAYERS):
            _is_google = "google.com" in _url
            folium.TileLayer(
                tiles=_url, attr=_attr, name=_name,
                max_zoom=20 if _is_google else 19,
                overlay=False,          # base layer → radio button ใน LayerControl
                control=True,
                show=(_i == 0),         # OpenStreetMap เปิดเป็น default
            ).add_to(m)

        # ── Plugins ───────────────────────────────────────────────────────────
        if opt_minimap:
            fp.MiniMap(toggle_display=True, position="bottomleft").add_to(m)
        if opt_measure:
            fp.MeasureControl(position="topleft", primary_length_unit="meters",
                secondary_length_unit="kilometers", primary_area_unit="sqmeters").add_to(m)
        fp.Fullscreen(position="topleft").add_to(m)
        fp.MousePosition(position="bottomright", separator=" | Lon: ", prefix="Lat: ").add_to(m)

        # ── เพิ่ม WMS/Overlay ทั้งหมด (overlay=True, show=False) ─────────────
        for (_name, _type, _url, _layers, _attr, _fmt, _transparent) in WMS_LAYERS:
            try:
                if _type == "wms":
                    folium.WmsTileLayer(
                        url=_url, layers=_layers,
                        fmt=_fmt, transparent=_transparent,
                        attr=_attr, name=_name,
                        overlay=True, control=True, show=False,
                    ).add_to(m)
                else:
                    folium.TileLayer(
                        tiles=_url, attr=_attr, name=_name,
                        overlay=True, control=True, show=False,
                    ).add_to(m)
            except Exception:
                pass

        # ── Data layers ───────────────────────────────────────────────────────
        has_vector = "gdf_loaded" in st.session_state and st.session_state.gdf_loaded is not None
        has_csv    = "csv_gdf"    in st.session_state and st.session_state.csv_gdf    is not None

        if has_vector:
            _gdf = st.session_state.gdf_loaded
            _ac  = [c for c in _gdf.columns if c != "geometry"]
            _tt  = _ac[:5] or None
            _pp  = _ac if opt_fullattr else _ac[:5]
            folium.GeoJson(
                _gdf.__geo_interface__, name="📂 Layer อัปโหลด",
                style_function=lambda x:{"fillColor":"#7A2020","color":"#7A2020","weight":2,"fillOpacity":0.3},
                tooltip=folium.GeoJsonTooltip(fields=_tt, aliases=[f"{c}:" for c in _tt], sticky=True) if _tt else None,
                popup=folium.GeoJsonPopup(fields=_pp, aliases=[f"<b>{c}</b>" for c in _pp], max_width=400) if _pp else None,
            ).add_to(m)

        if has_csv:
            _cgdf = st.session_state.csv_gdf
            _cac  = [c for c in _cgdf.columns if c not in ("geometry","_lat","_lon")]
            _cont = fp.MarkerCluster(name="📍 CSV Points") if opt_cluster else folium.FeatureGroup(name="📍 CSV Points")
            for _, _row in _cgdf.iterrows():
                _ph = "<table style='font-size:11px'>" + "".join(
                    f"<tr><td><b>{c}</b></td><td>{_row[c]}</td></tr>"
                    for c in (_cac if opt_fullattr else _cac[:4])) + "</table>"
                folium.CircleMarker(
                    [_row.geometry.y, _row.geometry.x],
                    radius=7, color="#7A2020", fill=True, fill_color="#7A2020", fill_opacity=0.8,
                    tooltip=str(_row[_cac[0]]) if _cac else "",
                    popup=folium.Popup(_ph, max_width=360),
                ).add_to(_cont)
            _cont.add_to(m)

        # Geocode marker
        if "geocode_results" in st.session_state:
            _gr = st.session_state["geocode_results"]
            if _gr:
                folium.Marker([float(_gr[0]["lat"]),float(_gr[0]["lon"])],
                    popup=_gr[0].get("display_name","")[:200], tooltip="🔍 ตำแหน่งที่ค้นหา",
                    icon=folium.Icon(color="red",icon="search",prefix="fa")).add_to(m)

        # Coord pin
        if "coord_target" in st.session_state:
            _t = st.session_state["coord_target"]
            folium.Marker([_t[0],_t[1]], popup=f"Lat {_t[0]:.6f}, Lon {_t[1]:.6f}",
                tooltip="📌 พิกัดที่ระบุ",
                icon=folium.Icon(color="blue",icon="map-marker",prefix="fa")).add_to(m)

        # ── User pins — draggable ─────────────────────────────────────────────
        if "pin_list" not in st.session_state:
            st.session_state["pin_list"] = []

        for _pi, (_plat, _plon, _plbl) in enumerate(st.session_state["pin_list"]):
            _pm = folium.Marker(
                [_plat, _plon],
                tooltip=f"📍 {_plbl}<br>{_plat:.5f}, {_plon:.5f}<br><i>ลากเพื่อย้าย</i>",
                popup=folium.Popup(
                    f"<b>{_plbl}</b><br>Lat: {_plat:.6f}<br>Lon: {_plon:.6f}",
                    max_width=200,
                ),
                icon=folium.Icon(color="orange", icon="thumb-tack", prefix="fa"),
                draggable=True,
            )
            _pm.add_to(m)

        # LayerControl
        folium.LayerControl(collapsed=True, position="topright").add_to(m)

        map_out = st_folium(m, use_container_width=True, height=660,
                            returned_objects=["last_clicked","last_object_clicked_popup"],
                            key="main_map")

        # ── Handle map click: auto-pin + drag-to-move ────────────────────────
        if map_out and map_out.get("last_clicked"):
            _lc   = map_out["last_clicked"]
            _clat = _lc["lat"]; _clon = _lc["lng"]
            # บันทึกพิกัดล่าสุดสำหรับ WMS GetFeatureInfo
            st.session_state["gfi_clat"] = _clat
            st.session_state["gfi_clon"] = _clon

            if st.session_state.get("opt_pin"):
                _pins = st.session_state["pin_list"]

                # ตรวจว่า click อยู่ใกล้ pin ที่มีอยู่แล้วไหม (รัศมี ~50 ม. = ~0.0005°)
                # ถ้าใช่ → user อาจ drag pin มาจุดนี้ → ไม่ปักใหม่
                _nearest_idx = None
                _min_dist = 999
                for _ii, (_pp, _qq, _) in enumerate(_pins):
                    _d = ((_pp-_clat)**2 + (_qq-_clon)**2)**0.5
                    if _d < _min_dist:
                        _min_dist = _d; _nearest_idx = _ii

                _too_close = _min_dist < 0.00001   # ซ้ำเป๊ะ (< 1 ม.)
                _near_pin  = _min_dist < 0.001      # ใกล้ pin เดิม ~100 ม.

                if _too_close:
                    pass  # คลิกซ้ำตำแหน่งเดิม — ไม่ทำอะไร
                elif _near_pin and _nearest_idx is not None and len(_pins) > 0:
                    # อาจเป็นการ drag pin มาใกล้ๆ → แสดงปุ่มให้เลือก
                    _old = _pins[_nearest_idx]
                    st.caption(f"📍 ใกล้ **{_old[2]}** ({_min_dist*111000:.0f} ม.) — คลิกใหม่ หรือกด 💾 ย้ายหมุด")
                    if st.button(f"💾 ย้าย {_old[2]} มาที่นี่", key="move_pin_btn"):
                        st.session_state["pin_list"][_nearest_idx] = (_clat, _clon, _old[2])
                        st.rerun()
                    if st.button(f"📍 ปักหมุดใหม่ ณ จุดนี้", key="new_pin_here"):
                        st.session_state["pin_list"].append((_clat, _clon, f"Pin {len(_pins)+1}"))
                        st.rerun()
                else:
                    # ไกลจาก pin เดิม → ปักหมุดใหม่ทันที
                    _n = f"Pin {len(_pins)+1}"
                    st.session_state["pin_list"].append((_clat, _clon, _n))
                    st.rerun()
            else:
                st.caption(f"📍 คลิกที่: **{_clat:.6f}**, **{_clon:.6f}**")

        if map_out and map_out.get("last_object_clicked_popup"):
            with st.expander("📋 ข้อมูล Feature ที่คลิก", expanded=True):
                st.markdown(map_out["last_object_clicked_popup"], unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Heatmap
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Heatmap + Marker Clustering
# ═══════════════════════════════════════════════════════════════════════════════
with tab_heatmap:
    st.subheader("🌡️ Heatmap / Marker Clustering")

    heat_csv = st.file_uploader("อัปโหลด CSV ที่มี Lat/Lon", type=["csv"], key="heat_csv")
    if heat_csv:
        st.session_state["heat_df"] = pd.read_csv(heat_csv)

    if "heat_df" in st.session_state:
        df_heat = st.session_state["heat_df"]

        # ── Mode selector ─────────────────────────────────────────────────────
        heat_mode = st.radio("โหมดแสดงผล",
            ["🌡️ Heatmap ความหนาแน่น", "📍 Marker Clustering"],
            horizontal=True, key="heat_mode")

        c1, c2, c3 = st.columns(3)
        lat_h    = c1.selectbox("Latitude col",  df_heat.columns.tolist(), key="heat_lat")
        lon_h    = c2.selectbox("Longitude col", df_heat.columns.tolist(), key="heat_lon")

        num_cols = ["(ไม่มี)"] + df_heat.select_dtypes(include="number").columns.tolist()

        if heat_mode == "🌡️ Heatmap ความหนาแน่น":
            weight_h = c3.selectbox("Weight (ค่าน้ำหนัก)", num_cols, key="heat_weight")
            radius   = st.slider("Radius", 5, 50, 15, key="heat_radius")
            blur     = st.slider("Blur",   5, 30, 15, key="heat_blur")
        else:  # Marker Clustering
            label_col = c3.selectbox("Label column (tooltip)", ["(ไม่มี)"] + df_heat.columns.tolist(), key="heat_label")
            popup_cols = st.multiselect("Popup columns (attribute)", df_heat.columns.tolist(), key="heat_popup")
            mk_color   = st.color_picker("สีจุด", "#7A2020", key="heat_mk_color")

        if st.button("▶️ สร้างแผนที่", type="primary", key="build_heat"):
            try:
                df_c = df_heat.copy()
                df_c["_lat"] = pd.to_numeric(df_c[lat_h], errors="coerce")
                df_c["_lon"] = pd.to_numeric(df_c[lon_h], errors="coerce")
                df_c = df_c.dropna(subset=["_lat","_lon"])
                if len(df_c) == 0:
                    st.error("ไม่พบข้อมูลพิกัดที่ valid")
                else:
                    st.session_state["heat_df_clean"] = df_c
                    st.session_state["heat_n"]        = len(df_c)
                    st.session_state["heat_center"]   = [df_c["_lat"].mean(), df_c["_lon"].mean()]
                    if heat_mode == "🌡️ Heatmap ความหนาแน่น":
                        if weight_h == "(ไม่มี)":
                            st.session_state["heat_data"] = df_c[["_lat","_lon"]].values.tolist()
                        else:
                            df_c["_w"] = pd.to_numeric(df_c[weight_h], errors="coerce").fillna(1)
                            st.session_state["heat_data"] = df_c[["_lat","_lon","_w"]].values.tolist()
                        st.session_state["heat_build_mode"] = "heatmap"
                    else:
                        st.session_state["heat_build_mode"] = "cluster"
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

        if "heat_df_clean" in st.session_state and st.session_state.get("heat_build_mode"):
            from folium.plugins import HeatMap, MarkerCluster, FastMarkerCluster
            df_c   = st.session_state["heat_df_clean"]
            center = st.session_state["heat_center"]
            n      = st.session_state["heat_n"]
            mode   = st.session_state["heat_build_mode"]

            m5 = folium.Map(location=center, zoom_start=8, tiles=None)
            folium.TileLayer("https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}",
                attr="© Google", name="🚗 Google Roads", show=True, max_zoom=20).add_to(m5)
            folium.TileLayer("https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                attr="© Google", name="🛰️ Google Hybrid", max_zoom=20).add_to(m5)
            folium.TileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                attr="© OpenStreetMap", name="🗺️ OpenStreetMap").add_to(m5)

            fp.Fullscreen(position="topleft").add_to(m5)
            fp.MousePosition(position="bottomright", separator=" | Lon: ", prefix="Lat: ").add_to(m5)
            fp.MeasureControl(position="topleft", primary_length_unit="meters",
                secondary_length_unit="kilometers", primary_area_unit="sqmeters").add_to(m5)

            if mode == "heatmap":
                _r = st.session_state.get("heat_radius", 15)
                _b = st.session_state.get("heat_blur",   15)
                HeatMap(st.session_state["heat_data"], radius=_r, blur=_b, min_opacity=0.4,
                    name="🌡️ Heatmap").add_to(m5)
                st.success(f"✅ Heatmap จาก **{n:,}** จุด")
            else:
                # Marker Clustering
                mc = MarkerCluster(name="📍 Marker Clusters", show=True)
                _lcol  = st.session_state.get("heat_label_col_val", "(ไม่มี)")
                _pcols = st.session_state.get("heat_popup_cols_val", [])
                _mkcol = st.session_state.get("heat_mk_color_val", "#7A2020")

                # ใช้ CircleMarker เพื่อแสดงสี
                for _, row in df_c.iterrows():
                    _tip = str(row[_lcol]) if _lcol != "(ไม่มี)" and _lcol in df_c.columns else f"{row['_lat']:.5f},{row['_lon']:.5f}"
                    _ph  = ""
                    if _pcols:
                        _ph = "<table style='font-size:11px'>" + "".join(
                            f"<tr><td><b>{c}</b></td><td>{row.get(c,'')}</td></tr>"
                            for c in _pcols if c in df_c.columns
                        ) + "</table>"
                    folium.CircleMarker(
                        [row["_lat"], row["_lon"]], radius=6,
                        color=_mkcol, fill=True, fill_color=_mkcol, fill_opacity=0.8,
                        tooltip=_tip,
                        popup=folium.Popup(_ph, max_width=320) if _ph else None,
                    ).add_to(mc)
                mc.add_to(m5)
                st.success(f"✅ Marker Cluster จาก **{n:,}** จุด")

            folium.LayerControl(collapsed=False).add_to(m5)
            st_folium(m5, use_container_width=True, height=580, key="heat_map")

        # บันทึก widget values ก่อน button press (ใช้ on_change workaround)
        if "heat_mode" in st.session_state:
            st.session_state["heat_label_col_val"]  = st.session_state.get("heat_label","(ไม่มี)")
            st.session_state["heat_popup_cols_val"]  = st.session_state.get("heat_popup",[])
            st.session_state["heat_mk_color_val"]    = st.session_state.get("heat_mk_color","#7A2020")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ตรวจสอบ/ประมวลผลข้อมูล
# ═══════════════════════════════════════════════════════════════════════════════
with tab_spatial:
    st.subheader("🔍 ตรวจสอบ/ประมวลผลข้อมูล")

    # ── helper: load any vector file ─────────────────────────────────────────
    def load_vector(upload, key_sfx=""):
        if upload is None: return None
        try:
            if upload.name.lower().endswith(".zip"):
                with tempfile.TemporaryDirectory() as tmp:
                    zp = os.path.join(tmp,"d.zip")
                    with open(zp,"wb") as f: f.write(upload.read())
                    with zipfile.ZipFile(zp) as z: z.extractall(tmp)
                    shps = [f for f in os.listdir(tmp) if f.endswith(".shp")]
                    if not shps: st.error("ไม่พบ .shp ใน zip"); return None
                    return gpd.read_file(os.path.join(tmp, shps[0]))
            else:
                return gpd.read_file(upload)
        except Exception as e:
            st.error(f"โหลดไม่ได้: {e}"); return None

    def load_csv_as_gdf(upload, lat_col, lon_col):
        df = pd.read_csv(upload)
        df["_lat"] = pd.to_numeric(df[lat_col], errors="coerce")
        df["_lon"] = pd.to_numeric(df[lon_col], errors="coerce")
        df = df.dropna(subset=["_lat","_lon"])
        return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["_lon"],df["_lat"]), crs="EPSG:4326")

    sp_tabs = st.tabs([
        "🗺️ แผนที่ + หลาย Layer",
        "⚙️ Geoprocessing",
        "📍 Point-in-Polygon",
        "📋 Query Attribute",
    ])
    sp_map, sp_geo, sp_pip, sp_query = sp_tabs

    # ─────────────────────────────────────────────────────────────────────────
    # SP_MAP — Interactive map with multi-layer upload
    # ─────────────────────────────────────────────────────────────────────────
    with sp_map:
        st.markdown("**แผนที่สำหรับตรวจสอบข้อมูล — อัปโหลดได้หลาย Layer**")

        _sp_col_ctrl, _sp_col_map = st.columns([1, 3], gap="small")

        with _sp_col_ctrl:
            # Basemap
            with st.expander("🗺️ Basemap", expanded=True):
                sp_basemap = st.radio("เลือก Basemap", [
                    "🚗 Google Roads", "🛰️ Google Hybrid",
                    "🗺️ OpenStreetMap", "🛰️ Esri Satellite",
                ], key="sp_basemap", label_visibility="collapsed")
            SP_BASEMAPS = {
                "🚗 Google Roads":    ("https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}", "© Google", 20),
                "🛰️ Google Hybrid":   ("https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", "© Google", 20),
                "🗺️ OpenStreetMap":   ("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png","© OpenStreetMap", 19),
                "🛰️ Esri Satellite":  ("https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}","© Esri", 19),
            }

            # Multi-layer upload
            with st.expander("📂 **อัปโหลด Layer**", expanded=True):
                st.caption("รองรับ GeoJSON, Shapefile (.zip), CSV Lat/Lon")

                # init layer store
                if "sp_layers" not in st.session_state:
                    st.session_state["sp_layers"] = {}  # {name: gdf}

                _sp_ftype = st.radio("ประเภท", ["GeoJSON/Shapefile","CSV Lat/Lon"],
                    horizontal=True, key="sp_ftype")
                _sp_up = st.file_uploader(
                    "เลือกไฟล์",
                    type=["geojson","json","zip","csv"],
                    key="sp_upload",
                )
                if _sp_ftype == "CSV Lat/Lon" and _sp_up:
                    _df_prev = pd.read_csv(_sp_up); _sp_up.seek(0)
                    _csp1,_csp2 = st.columns(2)
                    _sp_lat = _csp1.selectbox("Lat col", _df_prev.columns.tolist(), key="sp_csv_lat")
                    _sp_lon = _csp2.selectbox("Lon col", _df_prev.columns.tolist(), key="sp_csv_lon")
                _sp_name = st.text_input("ชื่อ Layer (ตั้งเอง)", key="sp_lname",
                    placeholder="เช่น โรงเรียน, ขอบเขต อบต.")

                if st.button("➕ เพิ่ม Layer", key="sp_add_layer"):
                    if _sp_up is None:
                        st.warning("กรุณาเลือกไฟล์ก่อน")
                    else:
                        try:
                            _lname = _sp_name.strip() or _sp_up.name
                            if _sp_ftype == "CSV Lat/Lon":
                                _sp_up.seek(0)
                                _new_gdf = load_csv_as_gdf(_sp_up, _sp_lat, _sp_lon)
                            else:
                                _new_gdf = load_vector(_sp_up)
                            if _new_gdf is not None:
                                _new_gdf = _new_gdf.to_crs("EPSG:4326")
                                st.session_state["sp_layers"][_lname] = _new_gdf
                                st.success(f"✅ เพิ่ม **{_lname}**: {len(_new_gdf):,} features")
                                st.rerun()
                        except Exception as _e:
                            st.error(str(_e))

                # Layer list + delete
                if st.session_state["sp_layers"]:
                    st.markdown("**Layer ที่โหลดแล้ว:**")
                    _COLORS = ["#e63946","#2a9d8f","#e9c46a","#f4a261","#264653","#6a4c93","#1982c4"]
                    for _li, (_ln, _lgdf) in enumerate(list(st.session_state["sp_layers"].items())):
                        _lc_hex = _COLORS[_li % len(_COLORS)]
                        _la, _lb = st.columns([4,1])
                        _la.markdown(f"<span style='color:{_lc_hex}'>●</span> **{_ln}** ({len(_lgdf):,})", unsafe_allow_html=True)
                        if _lb.button("🗑️", key=f"sp_del_{_li}"):
                            del st.session_state["sp_layers"][_ln]; st.rerun()

            # Map options
            with st.expander("⚙️ ตัวเลือก", expanded=False):
                sp_cluster   = st.toggle("🔵 Cluster Point Layer", value=True,  key="sp_cluster")
                sp_fullattr  = st.toggle("📋 Popup เต็ม attribute", value=True, key="sp_fullattr")
                sp_minimap   = st.toggle("🗺️ Mini Map",  value=False, key="sp_minimap")

        with _sp_col_map:
            _sp_bm = SP_BASEMAPS[sp_basemap]
            m_sp = folium.Map(location=[13.0, 101.0], zoom_start=6,
                tiles=_sp_bm[0], attr=_sp_bm[1], max_zoom=_sp_bm[2], control_scale=True)

            fp.Fullscreen(position="topleft").add_to(m_sp)
            fp.MousePosition(position="bottomright", separator=" | Lon: ", prefix="Lat: ").add_to(m_sp)
            fp.MeasureControl(position="topleft", primary_length_unit="meters",
                secondary_length_unit="kilometers", primary_area_unit="sqmeters").add_to(m_sp)
            if sp_minimap:
                fp.MiniMap(toggle_display=True, position="bottomleft").add_to(m_sp)

            _COLORS = ["#e63946","#2a9d8f","#e9c46a","#f4a261","#264653","#6a4c93","#1982c4"]
            _all_bounds = []

            for _li, (_ln, _lgdf) in enumerate(st.session_state.get("sp_layers",{}).items()):
                _lc = _COLORS[_li % len(_COLORS)]
                _ac = [c for c in _lgdf.columns if c not in ("geometry","_lat","_lon")]
                _gtype = _lgdf.geom_type.iloc[0] if len(_lgdf) > 0 else "Unknown"

                if "Point" in _gtype:
                    if sp_cluster:
                        _mc_sp = fp.MarkerCluster(name=f"📍 {_ln}")
                        for _, _row in _lgdf.iterrows():
                            _ph = "<table style='font-size:11px'>" + "".join(
                                f"<tr><td><b>{c}</b></td><td>{_row.get(c,'')}</td></tr>"
                                for c in (_ac if sp_fullattr else _ac[:5])
                            ) + "</table>"
                            folium.CircleMarker(
                                [_row.geometry.y, _row.geometry.x], radius=6,
                                color=_lc, fill=True, fill_color=_lc, fill_opacity=0.8,
                                tooltip=str(_row[_ac[0]]) if _ac else "",
                                popup=folium.Popup(_ph, max_width=320),
                            ).add_to(_mc_sp)
                        _mc_sp.add_to(m_sp)
                    else:
                        _fg_sp = folium.FeatureGroup(name=f"📍 {_ln}")
                        for _, _row in _lgdf.iterrows():
                            _ph = "<table style='font-size:11px'>" + "".join(
                                f"<tr><td><b>{c}</b></td><td>{_row.get(c,'')}</td></tr>"
                                for c in (_ac if sp_fullattr else _ac[:5])
                            ) + "</table>"
                            folium.CircleMarker(
                                [_row.geometry.y, _row.geometry.x], radius=6,
                                color=_lc, fill=True, fill_color=_lc, fill_opacity=0.8,
                                tooltip=str(_row[_ac[0]]) if _ac else "",
                                popup=folium.Popup(_ph, max_width=320),
                            ).add_to(_fg_sp)
                        _fg_sp.add_to(m_sp)
                else:
                    folium.GeoJson(
                        _lgdf.__geo_interface__, name=f"🗂 {_ln}",
                        style_function=lambda x, c=_lc: {
                            "color":c, "fillColor":c, "weight":2, "fillOpacity":0.25},
                        tooltip=folium.GeoJsonTooltip(fields=_ac[:4]) if _ac else None,
                        popup=folium.GeoJsonPopup(
                            fields=_ac if sp_fullattr else _ac[:6],
                            aliases=[f"<b>{c}</b>" for c in (_ac if sp_fullattr else _ac[:6])],
                            max_width=400,
                        ) if _ac else None,
                    ).add_to(m_sp)

                try:
                    _b = _lgdf.total_bounds
                    _all_bounds.append(_b)
                except: pass

            # Auto-fit bounds
            if _all_bounds:
                import numpy as np
                _bb = np.array(_all_bounds)
                _sw = [float(_bb[:,1].min()), float(_bb[:,0].min())]
                _ne = [float(_bb[:,3].max()), float(_bb[:,2].max())]
                m_sp.fit_bounds([_sw, _ne])

            if st.session_state.get("sp_layers"):
                folium.LayerControl(collapsed=False, position="topright").add_to(m_sp)

            _sp_out = st_folium(m_sp, use_container_width=True, height=650,
                returned_objects=["last_clicked","last_object_clicked_popup"],
                key="sp_map")

            if _sp_out and _sp_out.get("last_clicked"):
                _slc = _sp_out["last_clicked"]
                st.caption(f"📍 คลิก: **{_slc['lat']:.6f}**, **{_slc['lng']:.6f}**")
            if _sp_out and _sp_out.get("last_object_clicked_popup"):
                with st.expander("📋 ข้อมูล Feature", expanded=True):
                    st.markdown(_sp_out["last_object_clicked_popup"], unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # SP_GEO — Geoprocessing
    # ─────────────────────────────────────────────────────────────────────────
    with sp_geo:
        st.markdown("**Geoprocessing — ประมวลผลเชิงพื้นที่ระหว่าง 2 Layer**")
        st.caption("รองรับ GeoJSON, Shapefile (.zip) สำหรับ Layer ที่เป็น Polygon")

        _ga, _gb = st.columns(2)
        with _ga:
            st.markdown("**Layer A**")
            up_a = st.file_uploader("Layer A", type=["geojson","json","zip"], key="geo_a")
        with _gb:
            st.markdown("**Layer B**")
            up_b = st.file_uploader("Layer B", type=["geojson","json","zip"], key="geo_b")

        geo_op = st.selectbox("ประเภท Geoprocessing", [
            "🔍 Intersection — พื้นที่ที่ทับซ้อนกัน",
            "➕ Union — รวม 2 layer",
            "➖ Difference — A ลบออก B",
            "🔄 Symmetric Difference — ส่วนที่ไม่ทับ",
            "📊 ตรวจสอบเท่านั้น (overlaps/intersects)",
        ], key="geo_op")

        if st.button("▶️ ประมวลผล", type="primary", key="run_geo"):
            _ga_gdf = load_vector(up_a)
            _gb_gdf = load_vector(up_b)
            if _ga_gdf is None or _gb_gdf is None:
                st.warning("กรุณาอัปโหลดทั้ง Layer A และ Layer B")
            else:
                try:
                    _gb_gdf = _gb_gdf.to_crs(_ga_gdf.crs)
                    if "Intersection" in geo_op:
                        _res = gpd.overlay(_ga_gdf, _gb_gdf, how="intersection", keep_geom_type=False)
                        _lbl = "Intersection"
                    elif "Union" in geo_op:
                        _res = gpd.overlay(_ga_gdf, _gb_gdf, how="union", keep_geom_type=False)
                        _lbl = "Union"
                    elif "Difference" in geo_op:
                        _res = gpd.overlay(_ga_gdf, _gb_gdf, how="difference", keep_geom_type=False)
                        _lbl = "Difference (A−B)"
                    elif "Symmetric" in geo_op:
                        _res = gpd.overlay(_ga_gdf, _gb_gdf, how="symmetric_difference", keep_geom_type=False)
                        _lbl = "Symmetric Difference"
                    else:  # ตรวจสอบเท่านั้น
                        _mask = _ga_gdf.intersects(_gb_gdf.unary_union)
                        st.session_state["geo_check"] = {
                            "n": int(_mask.sum()), "total": len(_ga_gdf),
                            "gdf_a": _ga_gdf, "gdf_b": _gb_gdf,
                        }
                        st.session_state.pop("geo_result", None)
                        st.rerun()

                    if len(_res) == 0:
                        st.session_state["geo_result"] = {"empty": True, "label": _lbl}
                    else:
                        _rp = _res.to_crs(epsg=32647)
                        _res["area_m2"]  = _rp.geometry.area.round(2)
                        _res["area_km2"] = (_rp.geometry.area / 1e6).round(6)
                        _res["area_rai"] = (_rp.geometry.area / 1600).round(2)
                        st.session_state["geo_result"] = {
                            "result": _res, "label": _lbl,
                            "gdf_a": _ga_gdf, "gdf_b": _gb_gdf,
                        }
                    st.session_state.pop("geo_check", None)
                    st.rerun()
                except Exception as _e:
                    st.error(f"Geoprocessing error: {_e}")

        # ── ผลลัพธ์ persistent ──
        if "geo_check" in st.session_state:
            _c = st.session_state["geo_check"]
            if _c["n"] > 0:
                st.success(f"✅ พบ **{_c['n']}/{_c['total']}** features ทับซ้อนกัน")
            else:
                st.info("ℹ️ ไม่มี feature ทับซ้อนกัน")
            _b = _c["gdf_a"].total_bounds
            _mc2 = folium.Map(location=[(_b[1]+_b[3])/2,(_b[0]+_b[2])/2], zoom_start=9)
            folium.GeoJson(_c["gdf_a"].__geo_interface__, name="Layer A",
                style_function=lambda x:{"color":"#e63946","fillColor":"#e63946","fillOpacity":0.2,"weight":2}).add_to(_mc2)
            folium.GeoJson(_c["gdf_b"].__geo_interface__, name="Layer B",
                style_function=lambda x:{"color":"#1a5276","fillColor":"#1a5276","fillOpacity":0.2,"weight":2}).add_to(_mc2)
            folium.LayerControl().add_to(_mc2)
            st_folium(_mc2, use_container_width=True, height=450, key="geo_check_map")

        if "geo_result" in st.session_state:
            _gr = st.session_state["geo_result"]
            if _gr.get("empty"):
                st.info(f"ℹ️ {_gr['label']}: ไม่มีพื้นที่ผลลัพธ์")
            else:
                _res = _gr["result"]; _lbl = _gr["label"]
                _tkm = _res["area_km2"].sum(); _tri = _res["area_rai"].sum()
                st.success(f"✅ **{_lbl}**: {len(_res):,} features · {_tkm:,.4f} km² ({_tri:,.2f} ไร่)")
                st.dataframe(_res.drop(columns="geometry"), use_container_width=True, hide_index=True)

                _b = _gr["gdf_a"].total_bounds
                _mr = folium.Map(location=[(_b[1]+_b[3])/2,(_b[0]+_b[2])/2], zoom_start=9)
                folium.GeoJson(_gr["gdf_a"].__geo_interface__, name="Layer A",
                    style_function=lambda x:{"color":"#e63946","fillColor":"#e63946","fillOpacity":0.15,"weight":2}).add_to(_mr)
                folium.GeoJson(_gr["gdf_b"].__geo_interface__, name="Layer B",
                    style_function=lambda x:{"color":"#1a5276","fillColor":"#1a5276","fillOpacity":0.15,"weight":2}).add_to(_mr)
                folium.GeoJson(_res.__geo_interface__, name=_lbl,
                    style_function=lambda x:{"color":"#28b463","fillColor":"#28b463","fillOpacity":0.5,"weight":2}).add_to(_mr)
                folium.LayerControl().add_to(_mr)
                st_folium(_mr, use_container_width=True, height=450, key="geo_result_map")
                st.download_button("⬇️ Export GeoJSON",
                    _res.to_crs(epsg=4326).to_json(),
                    f"{_lbl.replace(' ','_')}.geojson", "application/json")

    # ─────────────────────────────────────────────────────────────────────────
    # SP_PIP — Point-in-Polygon
    # ─────────────────────────────────────────────────────────────────────────
    with sp_pip:
        st.markdown("**ตรวจสอบว่าจุด (Lat/Lon) อยู่ใน Polygon ไหน**")
        pip_src  = st.radio("แหล่งข้อมูลจุด", ["พิมพ์พิกัดเอง","อัปโหลด CSV"],
            horizontal=True, key="pip_src")
        pip_poly = st.file_uploader("Polygon Layer (GeoJSON / .zip)",
            type=["geojson","json","zip"], key="pip_poly")

        if pip_src == "พิมพ์พิกัดเอง":
            _pc1,_pc2 = st.columns(2)
            pip_lat = _pc1.number_input("Latitude",  value=13.7563,  format="%.6f", key="pip_lat")
            pip_lon = _pc2.number_input("Longitude", value=100.5018, format="%.6f", key="pip_lon")
            points_data = [(pip_lat, pip_lon, "จุดที่ป้อน")]
        else:
            pip_csv = st.file_uploader("CSV (Lat, Lon)", type=["csv"], key="pip_csv")
            if pip_csv:
                df_pip = pd.read_csv(pip_csv)
                st.dataframe(df_pip.head(3), use_container_width=True, hide_index=True)
                _pp1,_pp2,_pp3 = st.columns(3)
                lat_c = _pp1.selectbox("Latitude col",  df_pip.columns, key="pip_lat_col")
                lon_c = _pp2.selectbox("Longitude col", df_pip.columns, key="pip_lon_col")
                lbl_c = _pp3.selectbox("Label col", ["(ไม่มี)"]+df_pip.columns.tolist(), key="pip_lbl_col")
                points_data = [
                    (row[lat_c], row[lon_c], str(row[lbl_c]) if lbl_c!="(ไม่มี)" else f"จุด {i+1}")
                    for i,(_,row) in enumerate(df_pip.dropna(subset=[lat_c,lon_c]).iterrows())
                ]
            else:
                points_data = []

        if st.button("🔍 ตรวจสอบ", type="primary", key="run_pip"):
            if pip_poly is None: st.warning("กรุณาอัปโหลด Polygon layer")
            elif not points_data: st.warning("กรุณาป้อนพิกัดหรืออัปโหลด CSV")
            else:
                try:
                    _poly_gdf = load_vector(pip_poly)
                    if _poly_gdf is None: st.error("โหลดไม่ได้")
                    else:
                        _poly_gdf = _poly_gdf.to_crs("EPSG:4326")
                        _acs = [c for c in _poly_gdf.columns if c!="geometry"]
                        _rows = []
                        for _lat,_lon,_lbl in points_data:
                            _pt = gpd.GeoDataFrame(geometry=[Point(_lon,_lat)], crs="EPSG:4326")
                            _jn = gpd.sjoin(_pt, _poly_gdf, how="left", predicate="within")
                            if _jn["index_right"].isna().all():
                                _rows.append({"จุด":_lbl,"Lat":_lat,"Lon":_lon,"สถานะ":"❌ นอก polygon"})
                            else:
                                _r = {"จุด":_lbl,"Lat":_lat,"Lon":_lon,"สถานะ":"✅ ใน polygon"}
                                for _c in _acs[:8]: _r[_c] = _jn.iloc[0].get(_c,"-")
                                _rows.append(_r)
                        st.session_state["pip_result"] = pd.DataFrame(_rows)
                        st.session_state["pip_poly_gdf"]    = _poly_gdf
                        st.session_state["pip_points_data"] = points_data
                        st.rerun()
                except Exception as _e:
                    st.error(f"Error: {_e}")

        if "pip_result" in st.session_state:
            _df_r = st.session_state["pip_result"]
            _pg   = st.session_state["pip_poly_gdf"]
            _pts  = st.session_state["pip_points_data"]
            st.dataframe(_df_r, use_container_width=True, hide_index=True)
            _b    = _pg.total_bounds
            _mpip = folium.Map(location=[(_b[1]+_b[3])/2,(_b[0]+_b[2])/2], zoom_start=9)
            _acs2 = [c for c in _pg.columns if c!="geometry"]
            folium.GeoJson(_pg.__geo_interface__, name="Polygon",
                style_function=lambda x:{"color":"#7A2020","fillColor":"#7A2020","fillOpacity":0.2,"weight":1.5},
                tooltip=folium.GeoJsonTooltip(fields=_acs2[:3]) if _acs2 else None,
            ).add_to(_mpip)
            for _lat,_lon,_lbl in _pts:
                _st = _df_r[_df_r["จุด"]==_lbl]["สถานะ"].values[0] if _lbl in _df_r["จุด"].values else ""
                folium.CircleMarker([_lat,_lon], radius=8,
                    color="green" if "✅" in str(_st) else "red",
                    fill=True, fill_opacity=0.9,
                    popup=f"<b>{_lbl}</b><br>{_st}").add_to(_mpip)
            folium.LayerControl().add_to(_mpip)
            st_folium(_mpip, use_container_width=True, height=450, key="pip_map")
            st.download_button("⬇️ Export CSV",
                _df_r.to_csv(index=False, encoding="utf-8-sig"), "pip_result.csv", "text/csv")

    # ─────────────────────────────────────────────────────────────────────────
    # SP_QUERY — Query Attribute
    # ─────────────────────────────────────────────────────────────────────────
    with sp_query:
        st.markdown("**กรอง / ค้นหา Feature ตาม Attribute**")
        st.caption("💡 อัปโหลด Layer ในแท็บ 🗺️ แผนที่ + หลาย Layer แล้วเลือกมาใช้ที่นี่ หรืออัปโหลดใหม่ได้เลย")

        # เลือกจาก sp_layers หรืออัปโหลดใหม่
        _q_src = st.radio("แหล่ง Layer", ["อัปโหลดใหม่","ใช้จากแผนที่ด้านบน"],
            horizontal=True, key="q_src")
        if _q_src == "ใช้จากแผนที่ด้านบน":
            _sp_layer_names = list(st.session_state.get("sp_layers",{}).keys())
            if not _sp_layer_names:
                st.warning("ยังไม่มี Layer — อัปโหลดในแท็บ 🗺️ ก่อน")
                gdf_q = None
            else:
                _q_pick = st.selectbox("เลือก Layer", _sp_layer_names, key="q_layer_pick")
                gdf_q   = st.session_state["sp_layers"][_q_pick]
        else:
            _q_up = st.file_uploader("อัปโหลด Layer", type=["geojson","json","zip"], key="q_up")
            if _q_up:
                gdf_q = load_vector(_q_up)
                if gdf_q is not None: st.session_state["q_gdf"] = gdf_q
            gdf_q = st.session_state.get("q_gdf")

        if gdf_q is not None:
            _qcols = [c for c in gdf_q.columns if c!="geometry"]
            st.markdown(f"**{len(gdf_q):,} features · {len(_qcols)} columns**")
            st.dataframe(gdf_q[_qcols].head(3), use_container_width=True, hide_index=True)

            _q_col  = st.selectbox("Column ที่จะกรอง", _qcols, key="q_col")
            _q_mode = st.radio("วิธีกรอง", ["เลือกค่า","Query String"],
                horizontal=True, key="q_mode")

            if _q_mode == "เลือกค่า":
                _q_vals = st.multiselect(f"ค่าของ {_q_col}",
                    sorted([str(v) for v in gdf_q[_q_col].dropna().unique()]), key="q_vals")
                if _q_vals and st.button("🔍 กรอง", type="primary", key="run_q"):
                    st.session_state["q_result"] = gdf_q[gdf_q[_q_col].astype(str).isin(_q_vals)]
                    st.rerun()
            else:
                st.caption("ตัวอย่าง: `PROVINCE == 'กรุงเทพมหานคร'` หรือ `AREA > 1000`")
                _q_str = st.text_input("Query String", key="q_str")
                if _q_str and st.button("🔍 Query", type="primary", key="run_qstr"):
                    try:
                        st.session_state["q_result"] = gdf_q.query(_q_str); st.rerun()
                    except Exception as _e:
                        st.error(f"Query error: {_e}")

            if "q_result" in st.session_state:
                _rq   = st.session_state["q_result"]
                _rcols = [c for c in _rq.columns if c!="geometry"]
                st.success(f"✅ พบ **{len(_rq):,}** features")
                st.dataframe(_rq[_rcols], use_container_width=True, hide_index=True)
                if len(_rq) > 0:
                    _b = _rq.total_bounds
                    _mq = folium.Map(location=[(_b[1]+_b[3])/2,(_b[0]+_b[2])/2], zoom_start=9)
                    folium.GeoJson(_rq.__geo_interface__,
                        style_function=lambda x:{"color":"#7A2020","fillColor":"#7A2020","fillOpacity":0.4,"weight":2},
                        tooltip=folium.GeoJsonTooltip(fields=_rcols[:3]) if _rcols else None,
                    ).add_to(_mq)
                    st_folium(_mq, use_container_width=True, height=400, key="q_map")
                    st.download_button("⬇️ Export GeoJSON",
                        _rq.to_json(), "query_result.geojson", "application/json")

    # ─────────────────────────────────────────────────────────────────────────
    # SP_DIST — วัดระยะห่าง
    # ─────────────────────────────────────────────────────────────────────────

with tab_arcgis:
    st.subheader("🏛️ ArcGIS Online Map Viewer")
    st.caption("ใช้ ArcGIS Map Viewer ตรงๆ ผ่าน iframe — ฟรี ไม่ต้อง login สำหรับ public maps")

    arcgis_mode = st.radio("โหมด", [
        "🗺️ ArcGIS Map Viewer",
        "🔍 ArcGIS Feature Search (Living Atlas)",
        "🌏 ArcGIS Thailand Open Data",
    ], horizontal=True, key="arcgis_mode")

    ARCGIS_URLS = {
        "🗺️ ArcGIS Map Viewer":
            "https://www.arcgis.com/apps/mapviewer/index.html",
        "🔍 ArcGIS Feature Search (Living Atlas)":
            "https://www.arcgis.com/home/search.html?q=thailand&t=content&f=Map",
        "🌏 ArcGIS Thailand Open Data":
            "https://www.arcgis.com/home/search.html?q=thailand+province&t=content&f=Layer",
    }

    arcgis_url = ARCGIS_URLS[arcgis_mode]

    # แสดง tips ตามโหมด
    if arcgis_mode == "🗺️ ArcGIS Map Viewer":
        with st.expander("💡 ArcGIS Map Viewer — feature หลัก"):
            st.markdown("""
| Feature | วิธีใช้ |
|---|---|
| 🗂️ เพิ่ม Layer | Add → Search for Layers → พิมพ์ชื่อ layer หรือ WMS URL |
| 🎨 เปลี่ยน Style | คลิก Layer → Styles → เลือก Smart Mapping |
| 🔍 Filter | คลิก Layer → Filter → สร้าง expression |
| 📊 Popup | คลิก Layer → Pop-ups → ปรับ field ที่แสดง |
| 📐 Measure | Settings toolbar → Measure |
| 🔢 Clustering | คลิก Layer → Clustering |
| 🖨️ Print | Contents → Save → Print |
| 🔗 Add WMS | Add → Add Layer from URL → ใส่ WMS URL |
            """)
        # tip เพิ่ม WMS Longdo
        st.info("💡 **เพิ่ม Longdo WMS:** Add → Add Layer from URL → `https://ms.longdo.com/mapproxy/service` → เลือก layer ที่ต้องการ")

    elif arcgis_mode == "🔍 ArcGIS Feature Search (Living Atlas)":
        st.info("🔍 ค้นหา layer สาธารณะจาก ArcGIS Living Atlas — มีข้อมูลไทยหลายชุด เช่น province boundary, population, flood")

    else:
        st.info("🌏 ค้นหา Open Data ของไทย — download หรือ Add to Map ได้เลย")

    st.markdown(f"**URL:** `{arcgis_url}`")
    st.components.v1.iframe(arcgis_url, height=650, scrolling=True)

    # ── แท็บย่อย: ArcGIS REST API layers ที่น่าสนใจ ─────────────────────────
    with st.expander("📋 ArcGIS REST Layers ของไทยที่ใช้ได้ฟรี"):
        st.markdown("""
| Layer | URL | วิธีใช้ |
|---|---|---|
| ขอบเขตจังหวัดไทย | `https://services5.arcgis.com/...` | Add to Map Viewer |
| Thailand Roads | ArcGIS Living Atlas | Search "thailand road" |
| Thailand Population | World Population | Search "world population" |
| Flood Risk Thailand | GISTDA | Search "thailand flood" |
| Land Cover Asia | Esri | Search "land cover asia" |

> **วิธีเพิ่ม WMS ไทยเข้า ArcGIS Map Viewer:**
> 1. Add → Add Layer from URL
> 2. ใส่ URL: `https://ms.longdo.com/mapproxy/service`
> 3. Type: WMS → Next
> 4. เลือก layer ที่ต้องการ (เช่น cityplan_dpt, dol, accident_3Bura_2564)
        """)

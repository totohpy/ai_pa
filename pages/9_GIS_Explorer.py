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
tab_map, tab_heatmap, tab_spatial, tab_kepler, tab_arcgis = st.tabs([
    "🗺️ แผนที่หลัก",
    "🌡️ Heatmap",
    "🔍 ตรวจสอบพื้นที่",
    "🌐 PyDeck",
    "🏛️ ArcGIS Viewer",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — แผนที่หลัก
# ═══════════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — แผนที่หลัก
# ═══════════════════════════════════════════════════════════════════════════════
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
            opt_pin      = st.toggle("📍 ปักหมุดจากการคลิก",   value=False, key="opt_pin")

        # ── รายการหมุด ───────────────────────────────────────────────────────
        if "pin_list" not in st.session_state:
            st.session_state["pin_list"] = []
        if opt_pin and st.session_state["pin_list"]:
            with st.expander(f"📍 หมุดที่ปัก ({len(st.session_state['pin_list'])})", expanded=True):
                for _i,(_plat,_plon,_plbl) in enumerate(st.session_state["pin_list"]):
                    _pc1,_pc2 = st.columns([4,1])
                    _pc1.caption(f"**{_plbl}** {_plat:.5f},{_plon:.5f}")
                    if _pc2.button("🗑️",key=f"dp{_i}"): st.session_state["pin_list"].pop(_i); st.rerun()
                if st.button("🗑️ ลบทั้งหมด",key="clrpins"): st.session_state["pin_list"]=[]; st.rerun()

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

        # User pins
        for _plat,_plon,_plbl in st.session_state.get("pin_list",[]):
            folium.Marker([_plat,_plon],
                popup=f"<b>{_plbl}</b><br>Lat {_plat:.6f}<br>Lon {_plon:.6f}",
                tooltip=_plbl,
                icon=folium.Icon(color="orange",icon="thumb-tack",prefix="fa")).add_to(m)

        # LayerControl — collapsed=True เพราะมี layer เยอะ
        folium.LayerControl(collapsed=True, position="topright").add_to(m)

        map_out = st_folium(m, use_container_width=True, height=660,
                            returned_objects=["last_clicked","last_object_clicked_popup"],
                            key="main_map")

        if map_out and map_out.get("last_clicked"):
            _lc = map_out["last_clicked"]
            _clat, _clon = _lc["lat"], _lc["lng"]
            st.caption(f"📍 คลิกที่: **{_clat:.6f}**, **{_clon:.6f}**")
            if st.session_state.get("opt_pin"):
                if st.button(f"📍 ปักหมุด ณ {_clat:.4f},{_clon:.4f}", key="add_pin_btn"):
                    _n = f"Pin {len(st.session_state['pin_list'])+1}"
                    st.session_state["pin_list"].append((_clat,_clon,_n)); st.rerun()

        if map_out and map_out.get("last_object_clicked_popup"):
            with st.expander("📋 ข้อมูล Feature ที่คลิก", expanded=True):
                st.markdown(map_out["last_object_clicked_popup"], unsafe_allow_html=True)

            with st.expander("📋 ข้อมูล Feature ที่คลิก", expanded=True):
                st.markdown(map_out["last_object_clicked_popup"], unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Heatmap
# ═══════════════════════════════════════════════════════════════════════════════
with tab_heatmap:
    st.subheader("🌡️ Heatmap ความหนาแน่น")
    heat_csv = st.file_uploader("อัปโหลด CSV ที่มี Lat/Lon", type=["csv"], key="heat_csv")

    if heat_csv:
        df_heat = pd.read_csv(heat_csv)
        c1, c2, c3 = st.columns(3)
        lat_h = c1.selectbox("Latitude", df_heat.columns.tolist(), key="heat_lat")
        lon_h = c2.selectbox("Longitude", df_heat.columns.tolist(), key="heat_lon")
        weight_h = c3.selectbox("Weight (ความหนาแน่น)", ["(นับจำนวนจุด)"] + df_heat.select_dtypes(include='number').columns.tolist(), key="heat_weight")

        radius = st.slider("Radius", 5, 50, 15, key="heat_radius")

        if st.button("🌡️ สร้าง Heatmap", type="primary"):
            try:
                from folium.plugins import HeatMap
                df_clean = df_heat.dropna(subset=[lat_h, lon_h])
                center = [df_clean[lat_h].mean(), df_clean[lon_h].mean()]
                m5 = folium.Map(location=center, zoom_start=8)

                if weight_h == "(นับจำนวนจุด)":
                    heat_data = [[row[lat_h], row[lon_h]] for _, row in df_clean.iterrows()]
                else:
                    heat_data = [[row[lat_h], row[lon_h], row[weight_h]] for _, row in df_clean.iterrows()]

                HeatMap(heat_data, radius=radius, blur=15, min_opacity=0.4).add_to(m5)
                st.success(f"✅ Heatmap จาก {len(df_clean):,} จุด")
                st_folium(m5, use_container_width=True, height=550, key="heat_map")
            except Exception as e:
                st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7 — ตรวจสอบพื้นที่ (Spatial Analysis)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_spatial:
    st.subheader("🔍 ตรวจสอบพื้นที่ทับซ้อนและตำแหน่ง")

    sp1, sp2, sp3, sp4, sp5 = st.tabs([
        "📐 Overlap (ทับซ้อน)",
        "📍 Point-in-Polygon",
        "📋 Query Attribute",
        "📏 วัดระยะห่าง",
        "🔍 WMS GetFeatureInfo",
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SP1 — Overlap: upload 2 layers แล้ว intersect
    # ─────────────────────────────────────────────────────────────────────────
    with sp1:
        st.markdown("**อัปโหลด 2 Layer แล้วตรวจสอบว่าทับซ้อนกันไหม**")
        st.caption("รองรับ GeoJSON และ Shapefile (.zip)")

        def load_vector(upload, key_suffix):
            """โหลด GeoJSON หรือ Shapefile zip → GeoDataFrame"""
            if upload is None:
                return None
            name = upload.name.lower()
            try:
                if name.endswith(".zip"):
                    with tempfile.TemporaryDirectory() as tmp:
                        zpath = os.path.join(tmp, "data.zip")
                        with open(zpath, "wb") as f: f.write(upload.read())
                        with zipfile.ZipFile(zpath) as z: z.extractall(tmp)
                        shps = [f for f in os.listdir(tmp) if f.endswith(".shp")]
                        if not shps: return None
                        return gpd.read_file(os.path.join(tmp, shps[0]))
                else:
                    return gpd.read_file(upload)
            except Exception as e:
                st.error(f"โหลดไม่ได้: {e}")
                return None

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Layer A**")
            up_a = st.file_uploader("Layer A (GeoJSON / .zip)", type=["geojson","json","zip"], key="ov_a")
        with col_b:
            st.markdown("**Layer B**")
            up_b = st.file_uploader("Layer B (GeoJSON / .zip)", type=["geojson","json","zip"], key="ov_b")

        op_type = st.selectbox("ประเภทการตรวจสอบ", [
            "🔍 Intersection — พื้นที่ที่ทับซ้อนกัน",
            "➕ Union — รวม 2 layer",
            "➖ Difference — A ลบออก B",
            "🔄 Symmetric Difference — ส่วนที่ไม่ทับ",
            "📊 ตรวจสอบเท่านั้น (overlaps/intersects)",
        ], key="op_type")

        if st.button("▶️ ประมวลผล", type="primary", key="run_overlap"):
            gdf_a = load_vector(up_a, "a")
            gdf_b = load_vector(up_b, "b")

            if gdf_a is None or gdf_b is None:
                st.warning("กรุณาอัปโหลดทั้ง 2 layer")
            else:
                try:
                    # reproject ให้ตรงกัน
                    gdf_b = gdf_b.to_crs(gdf_a.crs)
                    gdf_a_proj = gdf_a.to_crs(epsg=32647)
                    gdf_b_proj = gdf_b.to_crs(epsg=32647)

                    if "Intersection" in op_type:
                        result = gpd.overlay(gdf_a, gdf_b, how="intersection", keep_geom_type=False)
                        label = "พื้นที่ทับซ้อน"
                    elif "Union" in op_type:
                        result = gpd.overlay(gdf_a, gdf_b, how="union", keep_geom_type=False)
                        label = "Union"
                    elif "Difference" in op_type:
                        result = gpd.overlay(gdf_a, gdf_b, how="difference", keep_geom_type=False)
                        label = "Difference (A-B)"
                    elif "Symmetric" in op_type:
                        result = gpd.overlay(gdf_a, gdf_b, how="symmetric_difference", keep_geom_type=False)
                        label = "Symmetric Difference"
                    else:
                        # ตรวจสอบ intersects เท่านั้น
                        overlap_mask = gdf_a.intersects(gdf_b.unary_union)
                        n_overlap = overlap_mask.sum()
                        n_total   = len(gdf_a)
                        if n_overlap > 0:
                            st.success(f"✅ พบ **{n_overlap}/{n_total}** features ของ Layer A ที่ทับซ้อนกับ Layer B")
                        else:
                            st.info("ℹ️ ไม่มี feature ทับซ้อนกัน")

                        # แสดงบนแผนที่
                        bounds = gdf_a.total_bounds
                        mc = [(bounds[1]+bounds[3])/2, (bounds[0]+bounds[2])/2]
                        mcheck = folium.Map(location=mc, zoom_start=9)
                        folium.GeoJson(gdf_a.__geo_interface__,
                            name="Layer A", style_function=lambda x: {
                                "color":"#7A2020","fillColor":"#7A2020","fillOpacity":0.2,"weight":2}
                        ).add_to(mcheck)
                        folium.GeoJson(gdf_b.__geo_interface__,
                            name="Layer B", style_function=lambda x: {
                                "color":"#1a5276","fillColor":"#1a5276","fillOpacity":0.2,"weight":2}
                        ).add_to(mcheck)
                        folium.LayerControl().add_to(mcheck)
                        st_folium(mcheck, use_container_width=True, height=450, key="check_map")
                        st.stop()

                    if len(result) == 0:
                        st.info("ℹ️ ไม่มีพื้นที่ทับซ้อน")
                    else:
                        result_proj = result.to_crs(epsg=32647)
                        result["area_m2"]  = result_proj.geometry.area.round(2)
                        result["area_km2"] = (result_proj.geometry.area / 1e6).round(4)
                        result["area_rai"] = (result_proj.geometry.area / 1600).round(2)
                        total_km2 = result["area_km2"].sum()
                        total_rai = result["area_rai"].sum()

                        st.success(f"✅ {label}: **{len(result):,} features** · รวม **{total_km2:,.4f} km²** ({total_rai:,.2f} ไร่)")
                        st.dataframe(result.drop(columns="geometry"), use_container_width=True, hide_index=True)

                        # แสดงบนแผนที่
                        bounds = gdf_a.total_bounds
                        mc = [(bounds[1]+bounds[3])/2, (bounds[0]+bounds[2])/2]
                        mres = folium.Map(location=mc, zoom_start=9)
                        folium.GeoJson(gdf_a.__geo_interface__, name="Layer A",
                            style_function=lambda x: {"color":"#7A2020","fillColor":"#7A2020","fillOpacity":0.15,"weight":2}
                        ).add_to(mres)
                        folium.GeoJson(gdf_b.__geo_interface__, name="Layer B",
                            style_function=lambda x: {"color":"#1a5276","fillColor":"#1a5276","fillOpacity":0.15,"weight":2}
                        ).add_to(mres)
                        folium.GeoJson(result.__geo_interface__, name=label,
                            style_function=lambda x: {"color":"#28b463","fillColor":"#28b463","fillOpacity":0.5,"weight":2}
                        ).add_to(mres)
                        folium.LayerControl().add_to(mres)
                        st_folium(mres, use_container_width=True, height=450, key="result_map")

                        st.download_button("⬇️ Export ผลลัพธ์ GeoJSON",
                            result.to_crs(epsg=4326).to_json(),
                            f"{label.replace(' ','_')}.geojson", "application/json")

                except Exception as e:
                    st.error(f"Error: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # SP2 — Point-in-Polygon
    # ─────────────────────────────────────────────────────────────────────────
    with sp2:
        st.markdown("**ตรวจสอบว่าจุด (Lat/Lon) อยู่ใน Polygon ไหน และ attribute อะไร**")

        pip_src = st.radio("แหล่งข้อมูลจุด", ["พิมพ์พิกัดเอง", "อัปโหลด CSV"], horizontal=True, key="pip_src")

        pip_poly = st.file_uploader("อัปโหลด Polygon Layer (GeoJSON / .zip)",
            type=["geojson","json","zip"], key="pip_poly")

        if pip_src == "พิมพ์พิกัดเอง":
            c1, c2 = st.columns(2)
            pip_lat = c1.number_input("Latitude", value=13.7563, format="%.6f", key="pip_lat")
            pip_lon = c2.number_input("Longitude", value=100.5018, format="%.6f", key="pip_lon")
            points_data = [(pip_lat, pip_lon, "จุดที่ป้อน")]
        else:
            pip_csv = st.file_uploader("CSV (มีคอลัมน์ Lat, Lon)", type=["csv"], key="pip_csv")
            if pip_csv:
                df_pip = pd.read_csv(pip_csv)
                st.dataframe(df_pip.head(3), use_container_width=True, hide_index=True)
                pc1, pc2, pc3 = st.columns(3)
                lat_c = pc1.selectbox("Latitude column", df_pip.columns, key="pip_lat_col")
                lon_c = pc2.selectbox("Longitude column", df_pip.columns, key="pip_lon_col")
                lbl_c = pc3.selectbox("Label column", ["(ไม่มี)"] + df_pip.columns.tolist(), key="pip_lbl_col")
                points_data = [
                    (row[lat_c], row[lon_c],
                     str(row[lbl_c]) if lbl_c != "(ไม่มี)" else f"จุด {i+1}")
                    for i, (_, row) in enumerate(df_pip.dropna(subset=[lat_c, lon_c]).iterrows())
                ]
            else:
                points_data = []

        if st.button("🔍 ตรวจสอบ", type="primary", key="run_pip"):
            if pip_poly is None:
                st.warning("กรุณาอัปโหลด Polygon layer")
            elif not points_data:
                st.warning("กรุณาป้อนพิกัดหรืออัปโหลด CSV")
            else:
                try:
                    gdf_poly = load_vector(pip_poly, "pip")
                    if gdf_poly is None:
                        st.error("โหลด Polygon ไม่ได้")
                    else:
                        gdf_poly = gdf_poly.to_crs(epsg=4326)
                        attr_cols = [c for c in gdf_poly.columns if c != "geometry"]

                        results_pip = []
                        for lat, lon, label in points_data:
                            pt = gpd.GeoDataFrame(geometry=[Point(lon, lat)], crs="EPSG:4326")
                            joined = gpd.sjoin(pt, gdf_poly, how="left", predicate="within")
                            if len(joined) == 0 or joined["index_right"].isna().all():
                                results_pip.append({"จุด": label, "Lat": lat, "Lon": lon,
                                                    "สถานะ": "❌ อยู่นอก polygon ทั้งหมด"})
                            else:
                                row_j = joined.iloc[0]
                                res = {"จุด": label, "Lat": lat, "Lon": lon, "สถานะ": "✅ อยู่ใน polygon"}
                                for col in attr_cols[:8]:  # แสดงสูงสุด 8 attribute
                                    res[col] = row_j.get(col, "-")
                                results_pip.append(res)

                        df_result = pd.DataFrame(results_pip)
                        st.dataframe(df_result, use_container_width=True, hide_index=True)

                        # แสดงบนแผนที่
                        bounds = gdf_poly.total_bounds
                        mc = [(bounds[1]+bounds[3])/2, (bounds[0]+bounds[2])/2]
                        mpip = folium.Map(location=mc, zoom_start=9)
                        folium.GeoJson(gdf_poly.__geo_interface__,
                            name="Polygon Layer",
                            style_function=lambda x: {"color":"#7A2020","fillColor":"#7A2020","fillOpacity":0.2,"weight":1.5},
                            tooltip=folium.GeoJsonTooltip(fields=attr_cols[:3]) if attr_cols else None
                        ).add_to(mpip)
                        for lat, lon, label in points_data:
                            row_info = df_result[df_result["จุด"]==label].iloc[0].to_dict() if label in df_result["จุด"].values else {}
                            status = row_info.get("สถานะ","")
                            color = "green" if "✅" in str(status) else "red"
                            folium.CircleMarker(
                                location=[lat, lon], radius=8,
                                color=color, fill=True, fill_color=color, fill_opacity=0.9,
                                popup=f"<b>{label}</b><br>{status}"
                            ).add_to(mpip)
                        folium.LayerControl().add_to(mpip)
                        st_folium(mpip, use_container_width=True, height=450, key="pip_map")

                        st.download_button("⬇️ Download ผลลัพธ์ CSV",
                            df_result.to_csv(index=False, encoding="utf-8-sig"),
                            "pip_result.csv", "text/csv")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # SP3 — Query Attribute
    # ─────────────────────────────────────────────────────────────────────────
    with sp3:
        st.markdown("**กรอง / ค้นหา Feature ตาม Attribute**")

        if "gdf_loaded" not in st.session_state or st.session_state.gdf_loaded is None:
            st.warning("⚠️ กรุณาอัปโหลด Shapefile/GeoJSON ในแท็บที่ 2 ก่อน")
        else:
            gdf_q = st.session_state.gdf_loaded
            attr_cols_q = [c for c in gdf_q.columns if c != "geometry"]

            st.markdown(f"Layer ปัจจุบัน: **{len(gdf_q):,} features** · {len(attr_cols_q)} columns")
            st.dataframe(gdf_q[attr_cols_q].head(3), use_container_width=True, hide_index=True)

            col_sel = st.selectbox("เลือก Column ที่จะกรอง", attr_cols_q, key="q_col")
            unique_vals = gdf_q[col_sel].dropna().unique().tolist()

            q_mode = st.radio("วิธีกรอง", ["เลือกค่า", "พิมพ์เงื่อนไข (query string)"], horizontal=True, key="q_mode")

            if q_mode == "เลือกค่า":
                sel_vals = st.multiselect(f"ค่าของ {col_sel}", sorted([str(v) for v in unique_vals]), key="q_vals")
                if sel_vals and st.button("🔍 กรอง", type="primary", key="run_query"):
                    result_q = gdf_q[gdf_q[col_sel].astype(str).isin(sel_vals)]
                    st.success(f"✅ พบ **{len(result_q):,}** features")
                    st.dataframe(result_q[attr_cols_q], use_container_width=True, hide_index=True)
                    # แสดงบนแผนที่
                    if len(result_q) > 0:
                        bounds = result_q.total_bounds
                        mc = [(bounds[1]+bounds[3])/2, (bounds[0]+bounds[2])/2]
                        mq = folium.Map(location=mc, zoom_start=9)
                        folium.GeoJson(result_q.__geo_interface__,
                            style_function=lambda x: {"color":"#7A2020","fillColor":"#7A2020","fillOpacity":0.4,"weight":2},
                            tooltip=folium.GeoJsonTooltip(fields=attr_cols_q[:3])
                        ).add_to(mq)
                        st_folium(mq, use_container_width=True, height=400, key="query_map")
                        st.download_button("⬇️ Export GeoJSON",
                            result_q.to_json(), "query_result.geojson", "application/json")
            else:
                st.caption("ตัวอย่าง: `PROVINCE == 'กรุงเทพมหานคร'` หรือ `AREA > 1000`")
                q_str = st.text_input("Query String", key="q_str",
                    placeholder="PROVINCE == 'กรุงเทพมหานคร'")
                if q_str and st.button("🔍 Query", type="primary", key="run_qstr"):
                    try:
                        result_q = gdf_q.query(q_str)
                        st.success(f"✅ พบ **{len(result_q):,}** features")
                        st.dataframe(result_q[attr_cols_q], use_container_width=True, hide_index=True)
                        if len(result_q) > 0:
                            bounds = result_q.total_bounds
                            mc = [(bounds[1]+bounds[3])/2, (bounds[0]+bounds[2])/2]
                            mq2 = folium.Map(location=mc, zoom_start=9)
                            folium.GeoJson(result_q.__geo_interface__,
                                style_function=lambda x: {"color":"#7A2020","fillColor":"#7A2020","fillOpacity":0.4,"weight":2},
                                tooltip=folium.GeoJsonTooltip(fields=attr_cols_q[:3])
                            ).add_to(mq2)
                            st_folium(mq2, use_container_width=True, height=400, key="qstr_map")
                            st.download_button("⬇️ Export GeoJSON",
                                result_q.to_json(), "query_result.geojson", "application/json")
                    except Exception as e:
                        st.error(f"Query error: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # SP4 — วัดระยะห่าง
    # ─────────────────────────────────────────────────────────────────────────
    with sp4:
        st.markdown("**วัดระยะห่างระหว่างจุดกับ Polygon boundary หรือระหว่างจุด 2 จุด**")

        dist_mode = st.radio("โหมด", [
            "📍 จุด → จุด",
            "📍 จุด → Polygon (ระยะถึง boundary)",
        ], horizontal=True, key="dist_mode")

        dc1, dc2 = st.columns(2)
        with dc1:
            st.markdown("**จุดที่ 1**")
            d_lat1 = st.number_input("Latitude", value=13.7563, format="%.6f", key="d_lat1")
            d_lon1 = st.number_input("Longitude", value=100.5018, format="%.6f", key="d_lon1")
        with dc2:
            if dist_mode == "📍 จุด → จุด":
                st.markdown("**จุดที่ 2**")
                d_lat2 = st.number_input("Latitude", value=13.8563, format="%.6f", key="d_lat2")
                d_lon2 = st.number_input("Longitude", value=100.6018, format="%.6f", key="d_lon2")
            else:
                st.markdown("**Polygon Layer**")
                dist_poly = st.file_uploader("GeoJSON / .zip", type=["geojson","json","zip"], key="dist_poly")

        if st.button("📏 วัดระยะ", type="primary", key="run_dist"):
            try:
                from shapely.geometry import Point as SPoint
                import math

                pt1 = SPoint(d_lon1, d_lat1)
                gpt1 = gpd.GeoDataFrame(geometry=[pt1], crs="EPSG:4326").to_crs(epsg=32647)

                if dist_mode == "📍 จุด → จุด":
                    pt2 = SPoint(d_lon2, d_lat2)
                    gpt2 = gpd.GeoDataFrame(geometry=[pt2], crs="EPSG:4326").to_crs(epsg=32647)
                    dist_m = gpt1.geometry[0].distance(gpt2.geometry[0])
                    st.success(f"📏 ระยะห่าง: **{dist_m:,.2f} เมตร** ({dist_m/1000:,.4f} กม.)")

                    # แผนที่
                    mdist = folium.Map(location=[(d_lat1+d_lat2)/2, (d_lon1+d_lon2)/2], zoom_start=10)
                    folium.Marker([d_lat1, d_lon1], popup="จุดที่ 1", icon=folium.Icon(color="red")).add_to(mdist)
                    folium.Marker([d_lat2, d_lon2], popup="จุดที่ 2", icon=folium.Icon(color="blue")).add_to(mdist)
                    folium.PolyLine([[d_lat1,d_lon1],[d_lat2,d_lon2]],
                        color="#7A2020", weight=2, dash_array="6",
                        tooltip=f"{dist_m:,.2f} ม.").add_to(mdist)
                    st_folium(mdist, use_container_width=True, height=400, key="dist_map")

                else:
                    if 'dist_poly' not in dir() or dist_poly is None:
                        st.warning("กรุณาอัปโหลด Polygon layer")
                    else:
                        gdf_dp = load_vector(dist_poly, "dp")
                        gdf_dp_proj = gdf_dp.to_crs(epsg=32647)
                        pt1_proj = gpt1.geometry[0]

                        gdf_dp_proj["dist_m"] = gdf_dp_proj.geometry.boundary.distance(pt1_proj).round(2)
                        gdf_dp_proj["dist_km"] = (gdf_dp_proj["dist_m"] / 1000).round(4)
                        nearest_idx = gdf_dp_proj["dist_m"].idxmin()
                        nearest = gdf_dp_proj.loc[nearest_idx]

                        attr_cols_d = [c for c in gdf_dp.columns if c != "geometry"]
                        st.success(f"📏 ระยะใกล้ที่สุด: **{nearest['dist_m']:,.2f} ม.** ({nearest['dist_km']:,.4f} กม.)")

                        result_dist = gdf_dp.copy()
                        result_dist["dist_m"] = gdf_dp_proj["dist_m"]
                        result_dist["dist_km"] = gdf_dp_proj["dist_km"]
                        st.dataframe(result_dist[attr_cols_d + ["dist_m","dist_km"]].sort_values("dist_m"),
                            use_container_width=True, hide_index=True)

                        bounds = gdf_dp.to_crs(epsg=4326).total_bounds
                        mc = [(bounds[1]+bounds[3])/2, (bounds[0]+bounds[2])/2]
                        mdist2 = folium.Map(location=mc, zoom_start=9)
                        folium.GeoJson(gdf_dp.to_crs(epsg=4326).__geo_interface__,
                            style_function=lambda x: {"color":"#7A2020","fillColor":"#7A2020","fillOpacity":0.2,"weight":1.5}
                        ).add_to(mdist2)
                        folium.CircleMarker([d_lat1, d_lon1], radius=8,
                            color="blue", fill=True, fill_color="blue",
                            popup="จุดที่ตรวจสอบ").add_to(mdist2)
                        st_folium(mdist2, use_container_width=True, height=400, key="dist_map2")

            except Exception as e:
                st.error(f"Error: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # SP5 — WMS GetFeatureInfo: คลิกแผนที่ → ถาม WMS server ว่า attribute อะไร
    # ─────────────────────────────────────────────────────────────────────────
    with sp5:
        st.markdown("**คลิกบนแผนที่ → ถาม WMS server ว่าตำแหน่งนั้นมีข้อมูลอะไร**")
        st.caption("ใช้ GetFeatureInfo request ไปยัง WMS server โดยตรง — รองรับเฉพาะ WMS ที่เปิด GetFeatureInfo")

        # ── เลือก WMS layer ──────────────────────────────────────────────────
        GFI_LAYERS = {
            "🗺️ Longdo Icons (ไทย)":           {"url": "https://ms.longdo.com/mapproxy/service", "layers": "longdo_icons"},
            "🏙️ ผังเมือง DPT":                  {"url": "https://ms.longdo.com/mapproxy/service", "layers": "cityplan_dpt"},
            "🏙️ ผังเมือง ทั่วประเทศ":            {"url": "https://ms.longdo.com/mapproxy/service", "layers": "cityplan_thailand"},
            "🏛️ กรมที่ดิน (DOL)":               {"url": "https://ms.longdo.com/mapproxy/service", "layers": "dol"},
            "🏛️ การใช้ที่ดิน LDD":              {"url": "https://ms.longdo.com/mapproxy/service", "layers": "ldd_landuse_2561_2563"},
            "🚗 อุบัติเหตุ 2564":               {"url": "https://ms.longdo.com/mapproxy/service", "layers": "accident_3Bura_2564"},
            "🇹🇭 RTSD แผนที่ฐาน":               {"url": "https://geoportal.rtsd.mi.th/arcgis/services/FGDS/Base_Map/MapServer/WMSServer", "layers": "0"},
            "🌳 กรมป่าไม้ (RFD)":               {"url": "https://gis.forest.go.th/arcgis/services/RFD_BASEMAP/MapServer/WMSServer", "layers": "0"},
            "🔧 กำหนด URL เอง":                  {"url": "", "layers": ""},
        }

        gfi_sel = st.selectbox("เลือก WMS Layer", list(GFI_LAYERS.keys()), key="gfi_layer_sel")
        gfi_cfg = GFI_LAYERS[gfi_sel]

        if gfi_sel == "🔧 กำหนด URL เอง":
            gc1, gc2 = st.columns(2)
            gfi_url    = gc1.text_input("WMS URL", key="gfi_url_custom")
            gfi_layers = gc2.text_input("Layer name", key="gfi_layers_custom")
        else:
            gfi_url    = gfi_cfg["url"]
            gfi_layers = gfi_cfg["layers"]

        st.info("👇 ป้อนพิกัดที่ต้องการสอบถาม (หรือคลิกบนแผนที่แล้วดูพิกัดจากแท็บอื่น)")

        g1, g2 = st.columns(2)
        gfi_lat = g1.number_input("Latitude", value=13.7563, format="%.6f", key="gfi_lat")
        gfi_lon = g2.number_input("Longitude", value=100.5018, format="%.6f", key="gfi_lon")

        gfi_fmt = st.selectbox("Response Format", [
            "text/plain", "text/html", "application/json", "text/xml"
        ], key="gfi_fmt")

        # ── แสดงแผนที่ preview พร้อม marker ─────────────────────────────────
        mgfi = folium.Map(location=[gfi_lat, gfi_lon], zoom_start=12)

        # เพิ่ม WMS layer ที่เลือก
        if gfi_url and gfi_layers:
            folium.raster_layers.WmsTileLayer(
                url=gfi_url,
                layers=gfi_layers,
                fmt="image/png",
                transparent=True,
                version="1.3.0",
                name=gfi_sel,
                show=True,
            ).add_to(mgfi)

        folium.Marker(
            [gfi_lat, gfi_lon],
            popup=f"Query point<br>({gfi_lat:.6f}, {gfi_lon:.6f})",
            icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
        ).add_to(mgfi)

        folium.LayerControl().add_to(mgfi)
        map_data = st_folium(mgfi, use_container_width=True, height=380, key="gfi_map")

        # ดึง Lat/Lon จากการคลิกแผนที่ (ถ้ามี)
        if map_data and map_data.get("last_clicked"):
            clicked = map_data["last_clicked"]
            gfi_lat = clicked["lat"]
            gfi_lon = clicked["lng"]
            st.success(f"📍 ตำแหน่งที่คลิก: **{gfi_lat:.6f}, {gfi_lon:.6f}** (ใช้พิกัดนี้สำหรับ query)")

        # ── ส่ง GetFeatureInfo request ────────────────────────────────────────
        if st.button("🔍 ขอข้อมูล GetFeatureInfo", type="primary", key="run_gfi"):
            if not gfi_url or not gfi_layers:
                st.warning("กรุณาระบุ WMS URL และ Layer name")
            else:
                try:
                    import requests as _req
                    from pyproj import Transformer

                    # แปลง Lat/Lon → pixel bbox สำหรับ WMS 1.3.0
                    # ใช้ bbox เล็กๆ รอบจุด (1 เมตร) ใน EPSG:4326
                    delta = 0.001  # ~100 ม.
                    bbox_str = f"{gfi_lat-delta},{gfi_lon-delta},{gfi_lat+delta},{gfi_lon+delta}"

                    params = {
                        "SERVICE":      "WMS",
                        "VERSION":      "1.3.0",
                        "REQUEST":      "GetFeatureInfo",
                        "LAYERS":       gfi_layers,
                        "QUERY_LAYERS": gfi_layers,
                        "STYLES":       "",
                        "CRS":          "EPSG:4326",
                        "BBOX":         bbox_str,
                        "WIDTH":        "101",
                        "HEIGHT":       "101",
                        "I":            "50",
                        "J":            "50",
                        "INFO_FORMAT":  gfi_fmt,
                        "FEATURE_COUNT":"10",
                    }

                    resp = _req.get(gfi_url, params=params, timeout=15)
                    resp.raise_for_status()
                    content = resp.text.strip()

                    st.markdown("---")
                    st.markdown(f"**📡 Response จาก WMS server** · HTTP {resp.status_code}")
                    st.caption(f"URL: `{resp.url[:120]}...`")

                    if not content or "no features" in content.lower() or content == "":
                        st.info("ℹ️ WMS server ตอบกลับ: ไม่พบข้อมูลที่ตำแหน่งนี้")
                    elif "text/plain" in gfi_fmt:
                        st.code(content, language="text")
                    elif "application/json" in gfi_fmt:
                        try:
                            import json
                            gfi_json = json.loads(content)
                            features = gfi_json.get("features", [])
                            if features:
                                st.success(f"✅ พบ {len(features)} feature(s)")
                                for i, feat in enumerate(features):
                                    with st.expander(f"Feature {i+1}"):
                                        props = feat.get("properties", {})
                                        st.json(props)
                            else:
                                st.info("ℹ️ ไม่พบ feature ที่ตำแหน่งนี้")
                                st.json(gfi_json)
                        except:
                            st.code(content, language="json")
                    elif "html" in gfi_fmt:
                        st.components.v1.html(content, height=300, scrolling=True)
                    else:
                        st.code(content, language="xml")

                    # ปุ่ม download raw response
                    ext = {"text/plain":"txt","text/html":"html",
                           "application/json":"json","text/xml":"xml"}.get(gfi_fmt,"txt")
                    st.download_button(
                        "⬇️ Download raw response",
                        content.encode("utf-8"),
                        f"gfi_response.{ext}",
                        gfi_fmt,
                        key="dl_gfi"
                    )

                except Exception as e:
                    st.error(f"GetFeatureInfo error: {e}")
                    st.caption("💡 WMS บางตัวไม่รองรับ GetFeatureInfo หรืออาจต้องการ API key")

        # ── Tips ──────────────────────────────────────────────────────────────
        with st.expander("💡 WMS layers ที่น่าจะรองรับ GetFeatureInfo"):
            st.markdown("""
| WMS Layer | โอกาสสำเร็จ | หมายเหตุ |
|---|---|---|
| Longdo cityplan_dpt | ⭐⭐⭐ | ข้อมูลผังเมือง อาจมี zone attribute |
| Longdo dol | ⭐⭐⭐ | ข้อมูลกรมที่ดิน |
| Longdo accident_* | ⭐⭐⭐ | ข้อมูลอุบัติเหตุ |
| RTSD แผนที่ฐาน | ⭐ | มักไม่เปิด GFI |
| กรมป่าไม้ RFD | ⭐⭐ | ขึ้นกับ server |

> หาก server ตอบ `no features found` อาจต้องลอง zoom เข้าแล้วใช้พิกัดที่แม่นขึ้น หรือ layer นั้นไม่รองรับ GFI
""")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 8 — PyDeck  (ArcGIS-style interactive 3D map)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_kepler:
    st.subheader("🌐 PyDeck — Interactive 3D Map Viewer")
    st.caption("แผนที่ interactive คุณภาพสูง คลิก feature → popup · 3D extrusion · color by attribute · built-in Streamlit")

    import pydeck as pdk

    pk_src = st.radio("แหล่งข้อมูล", ["CSV Lat/Lon", "GeoJSON / Shapefile"], horizontal=True, key="pk_src")

    pk_style = st.selectbox("Basemap style", [
        "mapbox://styles/mapbox/dark-v10",
        "mapbox://styles/mapbox/light-v10",
        "mapbox://styles/mapbox/satellite-v9",
        "mapbox://styles/mapbox/streets-v12",
        "mapbox://styles/mapbox/outdoors-v12",
    ], key="pk_style",
    format_func=lambda x: x.split("/")[-1].replace("-v10","").replace("-v9","").replace("-v12","").replace("-v11","").title()
    )

    pk_layer_type = st.selectbox("Layer type", [
        "ScatterplotLayer (จุด)",
        "HeatmapLayer (ความหนาแน่น)",
        "HexagonLayer (3D Hex)",
        "GridLayer (3D Grid)",
        "GeoJsonLayer (Vector)",
    ], key="pk_layer_type")

    if pk_src == "CSV Lat/Lon":
        pk_csv = st.file_uploader("อัปโหลด CSV", type=["csv"], key="pk_csv")
        if pk_csv:
            df_pk = pd.read_csv(pk_csv)
            st.dataframe(df_pk.head(3), use_container_width=True, hide_index=True)
            pc1, pc2 = st.columns(2)
            pk_lat = pc1.selectbox("Latitude col", df_pk.columns, key="pk_lat")
            pk_lon = pc2.selectbox("Longitude col", df_pk.columns, key="pk_lon")
            # Guard: ตรวจว่า column ที่เลือกยังมีอยู่ใน DataFrame
            if pk_lat not in df_pk.columns or pk_lon not in df_pk.columns:
                st.warning("⚠️ กรุณาเลือก Latitude/Longitude column ให้ถูกต้อง")
                st.stop()
            # สร้าง lat/lon columns โดยตรงแทนการ rename เพื่อหลีกเลี่ยง KeyError
            df_pk = df_pk.copy()
            df_pk["lat"] = pd.to_numeric(df_pk[pk_lat], errors="coerce")
            df_pk["lon"] = pd.to_numeric(df_pk[pk_lon], errors="coerce")
            df_pk = df_pk.dropna(subset=["lat", "lon"])

            # color picker
            cc1, cc2, cc3 = st.columns(3)
            pk_r = cc1.slider("Red",   0, 255, 122, key="pk_r")
            pk_g = cc2.slider("Green", 0, 255,  32, key="pk_g")
            pk_b = cc3.slider("Blue",  0, 255,  32, key="pk_b")

            mid_lat = df_pk["lat"].mean()
            mid_lon = df_pk["lon"].mean()

            view = pdk.ViewState(latitude=mid_lat, longitude=mid_lon,
                                  zoom=6, pitch=45 if "3D" in pk_layer_type or "Hex" in pk_layer_type or "Grid" in pk_layer_type else 0)

            if "Scatter" in pk_layer_type:
                # tooltip fields = all non-lat/lon columns
                extra_cols = [c for c in df_pk.columns if c not in ["lat","lon"]]
                tooltip_html = "<b>📍 จุด</b><br>" + "<br>".join(
                    [f"<b>{c}</b>: {{{c}}}" for c in extra_cols[:6]]
                )
                layer = pdk.Layer(
                    "ScatterplotLayer", df_pk,
                    get_position=["lon","lat"],
                    get_color=[pk_r, pk_g, pk_b, 200],
                    get_radius=500,
                    pickable=True,
                    auto_highlight=True,
                )
            elif "Heatmap" in pk_layer_type:
                layer = pdk.Layer(
                    "HeatmapLayer", df_pk,
                    get_position=["lon","lat"],
                    aggregation="MEAN",
                    pickable=False,
                )
                tooltip_html = None
            elif "Hex" in pk_layer_type:
                pk_elev = st.slider("Elevation scale", 1, 500, 50, key="pk_elev")
                layer = pdk.Layer(
                    "HexagonLayer", df_pk,
                    get_position=["lon","lat"],
                    radius=5000,
                    elevation_scale=pk_elev,
                    elevation_range=[0, 3000],
                    pickable=True,
                    extruded=True,
                    color_range=[
                        [254,237,222],[253,190,133],[253,141,60],
                        [230,85,13],[166,54,3],[102,37,6]
                    ],
                )
                tooltip_html = "<b>จำนวน:</b> {elevationValue}"
            else:  # Grid
                pk_elev = st.slider("Elevation scale", 1, 500, 50, key="pk_elev_g")
                layer = pdk.Layer(
                    "GridLayer", df_pk,
                    get_position=["lon","lat"],
                    cell_size=5000,
                    elevation_scale=pk_elev,
                    pickable=True,
                    extruded=True,
                )
                tooltip_html = "<b>จำนวน:</b> {count}"

            tooltip = {"html": tooltip_html, "style": {"background":"#2d2d2d","color":"white","fontSize":"12px","padding":"8px"}} if tooltip_html else None
            deck = pdk.Deck(layers=[layer], initial_view_state=view,
                            map_style=pk_style, tooltip=tooltip)
            st.pydeck_chart(deck, use_container_width=True)

            # attribute table
            with st.expander("📋 Attribute Table"):
                st.dataframe(df_pk, use_container_width=True, hide_index=True)
        else:
            # แสดง demo map เปล่า
            view = pdk.ViewState(latitude=13.7563, longitude=100.5018, zoom=5, pitch=30)
            deck = pdk.Deck(initial_view_state=view, map_style=pk_style,
                            layers=[], tooltip=None)
            st.pydeck_chart(deck, use_container_width=True)
            st.info("👆 อัปโหลด CSV เพื่อเริ่มต้น")

    else:  # GeoJSON / Shapefile
        pk_vec = st.file_uploader("GeoJSON / Shapefile (.zip)", type=["geojson","json","zip"], key="pk_vec")
        if pk_vec:
            try:
                name_pk = pk_vec.name.lower()
                if name_pk.endswith(".zip"):
                    with tempfile.TemporaryDirectory() as tmp:
                        zp = os.path.join(tmp, "d.zip")
                        with open(zp, "wb") as f: f.write(pk_vec.read())
                        with zipfile.ZipFile(zp) as z: z.extractall(tmp)
                        shps = [f for f in os.listdir(tmp) if f.endswith(".shp")]
                        gdf_pk = gpd.read_file(os.path.join(tmp, shps[0]))
                else:
                    gdf_pk = gpd.read_file(pk_vec)

                gdf_pk = gdf_pk.to_crs(epsg=4326)
                attr_cols_pk = [c for c in gdf_pk.columns if c != "geometry"]

                # color col
                cc1, cc2 = st.columns(2)
                pk_r2 = cc1.slider("Fill Red",   0,255,122,key="pk_r2")
                pk_g2 = cc1.slider("Fill Green", 0,255, 32,key="pk_g2")
                pk_b2 = cc2.slider("Fill Blue",  0,255, 32,key="pk_b2")
                pk_op  = cc2.slider("Opacity %", 0,100, 40,key="pk_op")

                tooltip_html = "<b>Feature</b><br>" + "<br>".join(
                    [f"<b>{c}</b>: {{{c}}}" for c in attr_cols_pk[:6]]
                )

                geojson_data = json.loads(gdf_pk.to_json())
                layer = pdk.Layer(
                    "GeoJsonLayer",
                    geojson_data,
                    pickable=True,
                    stroked=True,
                    filled=True,
                    extruded=False,
                    get_fill_color=[pk_r2, pk_g2, pk_b2, int(pk_op*2.55)],
                    get_line_color=[pk_r2, pk_g2, pk_b2, 220],
                    line_width_min_pixels=1,
                    auto_highlight=True,
                    highlight_color=[255, 200, 0, 180],
                )

                bounds = gdf_pk.total_bounds
                mid_lat = (bounds[1]+bounds[3])/2
                mid_lon = (bounds[0]+bounds[2])/2
                view = pdk.ViewState(latitude=mid_lat, longitude=mid_lon, zoom=6, pitch=0)

                deck = pdk.Deck(
                    layers=[layer], initial_view_state=view,
                    map_style=pk_style,
                    tooltip={"html": tooltip_html,
                             "style": {"background":"#2d2d2d","color":"white","fontSize":"12px","padding":"8px"}},
                )
                st.pydeck_chart(deck, use_container_width=True)

                with st.expander("📋 Attribute Table"):
                    st.dataframe(gdf_pk[attr_cols_pk], use_container_width=True, hide_index=True)

            except Exception as e:
                st.error(f"โหลดไม่ได้: {e}")
        else:
            view = pdk.ViewState(latitude=13.7563, longitude=100.5018, zoom=5, pitch=30)
            st.pydeck_chart(pdk.Deck(initial_view_state=view, map_style=pk_style), use_container_width=True)
            st.info("👆 อัปโหลด GeoJSON หรือ Shapefile เพื่อเริ่มต้น")

    with st.expander("💡 วิธีใช้ PyDeck"):
        st.markdown("""
| Layer Type | ใช้เมื่อ |
|---|---|
| ScatterplotLayer | จุดทั่วไป คลิกดู attribute |
| HeatmapLayer | ดูความหนาแน่น / cluster |
| HexagonLayer 3D | นับจำนวนจุดต่อพื้นที่ แบบ 3D |
| GridLayer 3D | เหมือน Hex แต่เป็นตาราง |
| GeoJsonLayer | Polygon/Line/Point จาก Shapefile |

**Tips:**
- 🖱️ คลิก feature → popup attribute
- 🔄 Ctrl+drag → หมุน 3D
- 🔍 Scroll → zoom
- 🎨 ปรับ RGB slider → เปลี่ยนสี real-time
        """)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 9 — ArcGIS Online Viewer
# ═══════════════════════════════════════════════════════════════════════════════
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

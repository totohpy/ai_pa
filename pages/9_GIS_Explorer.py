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
tab_map, tab_shape, tab_csv, tab_choropleth, tab_heatmap, tab_geo, tab_spatial, tab_kepler, tab_arcgis = st.tabs([
    "🗺️ แผนที่หลัก",
    "📂 Shapefile / GeoJSON",
    "📍 CSV Lat/Lon",
    "🎨 Choropleth Map",
    "🌡️ Heatmap",
    "🔧 Geoprocessing",
    "🔍 ตรวจสอบพื้นที่",
    "🌐 Kepler.gl",
    "🏛️ ArcGIS Viewer",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — แผนที่หลัก
# ═══════════════════════════════════════════════════════════════════════════════
with tab_map:
    st.subheader("🗺️ แผนที่ Interactive")

    # ── ค่าเริ่มต้นคงที่ ──────────────────────────────────────────────────────
    CENTER_LAT, CENTER_LON, ZOOM = 13.7563, 100.5018, 6

    # ── WMS/WMTS Overlay Catalog ──────────────────────────────────────────────
    LONGDO_URL = "https://ms.longdo.com/mapproxy/service"

    WMS_CATALOG = {
        # ── 🗺️ Longdo Map Styles ──────────────────────────────────────────────
        "🗺️ Longdo Icons (ภาษาไทย)":          {"type":"wms","url":LONGDO_URL,"layers":"longdo_icons","attr":"© Longdo Map","fmt":"image/png","transparent":True},
        "🗺️ Longdo Icons (English)":           {"type":"wms","url":LONGDO_URL,"layers":"longdo_icons_en","attr":"© Longdo Map","fmt":"image/png","transparent":True},
        "🗺️ Longdo Political (ไทย)":           {"type":"wms","url":LONGDO_URL,"layers":"longdo_political","attr":"© Longdo Map","fmt":"image/png","transparent":True},
        "🗺️ Longdo Political (English)":        {"type":"wms","url":LONGDO_URL,"layers":"longdo_political_en","attr":"© Longdo Map","fmt":"image/png","transparent":True},
        "🗺️ Longdo Gray (ไทย)":                {"type":"wms","url":LONGDO_URL,"layers":"longdo_gray","attr":"© Longdo Map","fmt":"image/png","transparent":True},
        "🗺️ Longdo Gray (English)":             {"type":"wms","url":LONGDO_URL,"layers":"longdo_gray_en","attr":"© Longdo Map","fmt":"image/png","transparent":True},
        "🗺️ Longdo Light (ไทย)":               {"type":"wms","url":LONGDO_URL,"layers":"longdo_light","attr":"© Longdo Map","fmt":"image/png","transparent":True},
        "🗺️ Longdo Light (English)":            {"type":"wms","url":LONGDO_URL,"layers":"longdo_light_en","attr":"© Longdo Map","fmt":"image/png","transparent":True},
        "🗺️ Longdo Dark (ไทย)":                {"type":"wms","url":LONGDO_URL,"layers":"longdo_dark","attr":"© Longdo Map","fmt":"image/png","transparent":True},
        "🗺️ Longdo Dark (English)":             {"type":"wms","url":LONGDO_URL,"layers":"longdo_dark_en","attr":"© Longdo Map","fmt":"image/png","transparent":True},

        # ── 🛰️ Longdo ภาพถ่ายดาวเทียม/อากาศ ────────────────────────────────
        "🛰️ Longdo Bluemarble Terrain":         {"type":"wms","url":LONGDO_URL,"layers":"bluemarble_terrain","attr":"© Longdo Map / GElib","fmt":"image/png","transparent":True},
        "🛰️ Thaichote (GISTDA 2560-2562)":      {"type":"wms","url":LONGDO_URL,"layers":"thaichote","attr":"© GISTDA / Longdo Map","fmt":"image/png","transparent":True},
        "🛰️ LDD Orthophoto (2547-2550)":        {"type":"wms","url":LONGDO_URL,"layers":"ldd_ortho","attr":"© กรมพัฒนาที่ดิน / Longdo Map","fmt":"image/png","transparent":True},

        # ── 🏙️ Longdo ผังเมือง ───────────────────────────────────────────────
        "🏙️ ผังเมือง ทั่วประเทศ (DPT+เมือง)":   {"type":"wms","url":LONGDO_URL,"layers":"cityplan_thailand","attr":"© กรมโยธาธิการ / Longdo Map","fmt":"image/png","transparent":True},
        "🏙️ ผังเมือง DPT":                      {"type":"wms","url":LONGDO_URL,"layers":"cityplan_dpt","attr":"© กรมโยธาธิการ / Longdo Map","fmt":"image/png","transparent":True},
        "🏙️ ผังเมือง ระดับจังหวัด":              {"type":"wms","url":LONGDO_URL,"layers":"cityplan_provinces","attr":"© Longdo Map","fmt":"image/png","transparent":True},
        "🏙️ ผังเมือง ระดับเมือง":               {"type":"wms","url":LONGDO_URL,"layers":"cityplan_cities","attr":"© Longdo Map","fmt":"image/png","transparent":True},

        # ── 🏛️ Longdo หน่วยงานราชการ ─────────────────────────────────────────
        "🏛️ กรมที่ดิน (DOL)":                   {"type":"wms","url":LONGDO_URL,"layers":"dol","attr":"© กรมที่ดิน / Longdo Map","fmt":"image/png","transparent":True},
        "🏛️ กรมที่ดิน HD":                      {"type":"wms","url":LONGDO_URL,"layers":"dol_hd","attr":"© กรมที่ดิน / Longdo Map","fmt":"image/png","transparent":True},
        "🏛️ กรมทางหลวง (DOH)":                  {"type":"wms","url":LONGDO_URL,"layers":"doh_section_km","attr":"© กรมทางหลวง / Longdo Map","fmt":"image/png","transparent":True},
        "🏛️ การใช้ที่ดิน LDD (2561-2563)":      {"type":"wms","url":LONGDO_URL,"layers":"ldd_landuse_2561_2563","attr":"© กรมพัฒนาที่ดิน / Longdo Map","fmt":"image/png","transparent":True},

        # ── 👥 Longdo ประชากร ─────────────────────────────────────────────────
        "👥 ประชากรไทย 2020":                   {"type":"wms","url":LONGDO_URL,"layers":"thailand_population","attr":"© Longdo Map","fmt":"image/png","transparent":True},
        "👥 FB Population (รวม)":               {"type":"wms","url":LONGDO_URL,"layers":"fb_population_2020","attr":"© Facebook / Longdo Map","fmt":"image/png","transparent":True},
        "👥 FB Population (ผู้สูงอายุ)":         {"type":"wms","url":LONGDO_URL,"layers":"fb_population_elderly","attr":"© Facebook / Longdo Map","fmt":"image/png","transparent":True},
        "👥 FB Population (เด็ก)":              {"type":"wms","url":LONGDO_URL,"layers":"fb_population_children","attr":"© Facebook / Longdo Map","fmt":"image/png","transparent":True},

        # ── 🚗 Longdo อุบัติเหตุ ──────────────────────────────────────────────
        "🚗 อุบัติเหตุ 2564 (3 หน่วยงาน)":      {"type":"wms","url":LONGDO_URL,"layers":"accident_3Bura_2564","attr":"© DGA / Longdo Map","fmt":"image/png","transparent":True},
        "🚗 อุบัติเหตุ 2563":                    {"type":"wms","url":LONGDO_URL,"layers":"accident_3Bura_2563","attr":"© DGA / Longdo Map","fmt":"image/png","transparent":True},
        "🚗 อุบัติเหตุ 2562":                    {"type":"wms","url":LONGDO_URL,"layers":"accident_3Bura_2562","attr":"© DGA / Longdo Map","fmt":"image/png","transparent":True},
        "🚗 อุบัติเหตุ iTIC 2564":               {"type":"wms","url":LONGDO_URL,"layers":"accident_itic_2564","attr":"© iTIC / Longdo Map","fmt":"image/png","transparent":True},

        # ── 🌊 Longdo น้ำท่วม/ความชัน ────────────────────────────────────────
        "🌊 น้ำท่วม GISTDA (realtime)":         {"type":"wms","url":LONGDO_URL,"layers":"gistda_flood_update","attr":"© GISTDA / Longdo Map","fmt":"image/png","transparent":True},
        "⛰️ ความชัน เกาะสมุย":                  {"type":"wms","url":LONGDO_URL,"layers":"samui_slope","attr":"© Longdo Map","fmt":"image/png","transparent":True},

        # ── 🇹🇭 หน่วยงานไทยอื่น ───────────────────────────────────────────────
        "🌳 กรมป่าไม้ (RFD Basemap)":            {"type":"wms","url":"https://gis.forest.go.th/arcgis/services/RFD_BASEMAP/MapServer/WMSServer","layers":"0","attr":"© กรมป่าไม้","fmt":"image/png","transparent":True},
        "🇹🇭 RTSD Orthophoto":                   {"type":"wms","url":"https://geoportal.rtsd.mi.th/arcgis/services/FGDS/Orthophoto/ImageServer/WMSServer","layers":"0","attr":"© กรมแผนที่ทหาร","fmt":"image/png","transparent":True},
        "🇹🇭 RTSD แผนที่ฐาน":                    {"type":"wms","url":"https://geoportal.rtsd.mi.th/arcgis/services/FGDS/Base_Map/MapServer/WMSServer","layers":"0","attr":"© กรมแผนที่ทหาร","fmt":"image/png","transparent":True},
        "🇹🇭 NSO สถิติ":                         {"type":"wms","url":"https://gis.nso.go.th/geoserver/wms","layers":"nso:province","attr":"© NSO Thailand","fmt":"image/png","transparent":True},

        # ── 🌍 นานาชาติ ───────────────────────────────────────────────────────
        "🌍 NASA GIBS MODIS Terra":              {"type":"tile","url":"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2024-01-01/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg","attr":"© NASA GIBS"},
        "🌍 NASA GIBS VIIRS Night Lights":       {"type":"tile","url":"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_DayNightBand_ENCC/default/2024-01-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.png","attr":"© NASA GIBS VIIRS"},
        "🌍 OpenTopoMap":                        {"type":"tile","url":"https://tile.opentopomap.org/{z}/{x}/{y}.png","attr":"© OpenTopoMap"},
        "🌍 Esri World Shaded Relief":           {"type":"tile","url":"https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}","attr":"© Esri"},
        "🌍 Esri World Street Map":              {"type":"tile","url":"https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}","attr":"© Esri"},
    }

    # ── Custom WMS (ย่อในแถวเดียว) ────────────────────────────────────────────
    with st.expander("➕ เพิ่ม WMS URL เอง", expanded=False):
        cw1, cw2, cw3 = st.columns([3, 2, 2])
        custom_url   = cw1.text_input("WMS URL", key="custom_wms_url",
            placeholder="https://example.com/geoserver/wms")
        custom_layer = cw2.text_input("Layer Name", key="custom_wms_layer",
            placeholder="workspace:layername")
        custom_attr  = cw3.text_input("Attribution", value="Custom WMS", key="custom_wms_attr")
        if custom_url and custom_layer:
            WMS_CATALOG["🔧 Custom WMS"] = {
                "type": "wms", "url": custom_url, "layers": custom_layer,
                "attr": custom_attr, "fmt": "image/png", "transparent": True,
            }

    # ── สร้างแผนที่ ───────────────────────────────────────────────────────────
    m = folium.Map(
        location=[CENTER_LAT, CENTER_LON],
        zoom_start=ZOOM,
        control_scale=True,
    )

    # เพิ่ม basemap ทั้งหมดเข้า LayerControl (ให้เลือกในแผนที่ได้เลย)
    BASEMAPS = {
        "OpenStreetMap":       ("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                                "© OpenStreetMap contributors"),
        "CartoDB Positron":    ("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                                "© CartoDB"),
        "CartoDB Dark Matter": ("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                                "© CartoDB"),
        "Stamen Terrain":      ("https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg",
                                "© Stamen Design"),
        "Stamen Toner":        ("https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.png",
                                "© Stamen Design"),
        "Esri Satellite":      ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                                "© Esri"),
    }
    for name, (url, attr) in BASEMAPS.items():
        folium.TileLayer(url, attr=attr, name=name, overlay=False, control=True).add_to(m)

    # เพิ่ม WMS/Tile overlays ที่ user เลือก (ถ้ามี custom)
    if "🔧 Custom WMS" in WMS_CATALOG and custom_url and custom_layer:
        cfg = WMS_CATALOG["🔧 Custom WMS"]
        try:
            folium.WmsTileLayer(
                url=cfg["url"], layers=cfg["layers"],
                fmt="image/png", transparent=True,
                attr=cfg["attr"], name="🔧 Custom WMS",
                overlay=True, control=True,
            ).add_to(m)
        except Exception as e:
            st.warning(f"⚠️ Custom WMS โหลดไม่ได้: {e}")

    # เพิ่ม WMS catalog ทั้งหมดเป็น overlay ให้เลือกใน LayerControl
    for layer_name, cfg in WMS_CATALOG.items():
        if layer_name == "🔧 Custom WMS":
            continue
        try:
            if cfg["type"] == "wms":
                folium.WmsTileLayer(
                    url=cfg["url"], layers=cfg["layers"],
                    fmt=cfg.get("fmt", "image/png"),
                    transparent=cfg.get("transparent", True),
                    attr=cfg["attr"], name=layer_name,
                    overlay=True, control=True, show=False,
                ).add_to(m)
            else:
                folium.TileLayer(
                    cfg["url"], attr=cfg["attr"],
                    name=layer_name, overlay=True,
                    control=True, show=False,
                ).add_to(m)
        except Exception:
            pass

    folium.LayerControl(collapsed=False, position="topright").add_to(m)

    # แสดง layer ที่ upload ไว้
    if "gdf_loaded" in st.session_state and st.session_state.gdf_loaded is not None:
        gdf = st.session_state.gdf_loaded
        folium.GeoJson(
            gdf.__geo_interface__,
            name="Shapefile/GeoJSON",
            style_function=lambda x: {
                "fillColor": "#7A2020", "color": "#7A2020",
                "weight": 2, "fillOpacity": 0.3
            },
            tooltip=folium.GeoJsonTooltip(fields=list(gdf.columns[:3]))
        ).add_to(m)
        st.info("✅ Layer จากแท็บ Shapefile/GeoJSON ถูกเพิ่มบนแผนที่")

    if "csv_gdf" in st.session_state and st.session_state.csv_gdf is not None:
        csv_gdf = st.session_state.csv_gdf
        for _, row in csv_gdf.iterrows():
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=6, color="#7A2020", fill=True, fill_opacity=0.7,
                popup=str(row.drop("geometry").to_dict())
            ).add_to(m)
        st.info("✅ Points จากแท็บ CSV Lat/Lon ถูกเพิ่มบนแผนที่")

    # ── Map options bar ───────────────────────────────────────────────────────
    mo1, mo2, mo3, mo4 = st.columns(4)
    opt_cluster  = mo1.toggle("🔵 Cluster จุด CSV",    value=True,  key="opt_cluster")
    opt_minimap  = mo2.toggle("🗺️ Mini Map",            value=False, key="opt_minimap")
    opt_measure  = mo3.toggle("📐 Measure tool",        value=False, key="opt_measure")
    opt_fullattr = mo4.toggle("📋 Popup เต็ม attribute",value=True,  key="opt_fullattr")

    # ── Search geocode ────────────────────────────────────────────────────────
    with st.expander("🔍 ค้นหาตำแหน่ง (Geocode)", expanded=False):
        sc1, sc2 = st.columns([4, 1])
        search_q = sc1.text_input("พิมพ์ชื่อสถานที่ (ไทย/อังกฤษ)", key="geocode_q",
                                   placeholder="กรุงเทพมหานคร, Chiang Mai, ...")
        if sc2.button("🔍 ค้นหา", key="geocode_btn") and search_q:
            try:
                import requests as _req
                r = _req.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": search_q, "format": "json", "limit": 5,
                            "accept-language": "th,en"},
                    headers={"User-Agent": "PA-GIS-Explorer/1.0"},
                    timeout=10,
                )
                geo_results = r.json()
                if geo_results:
                    st.session_state["geocode_results"] = geo_results
                    st.session_state["geocode_selected"] = 0
                else:
                    st.warning("ไม่พบตำแหน่ง")
            except Exception as e:
                st.error(f"Geocode error: {e}")

        if "geocode_results" in st.session_state:
            res = st.session_state["geocode_results"]
            labels = [f"{r.get('display_name','')[:80]}" for r in res]
            sel = st.selectbox("เลือกตำแหน่ง", labels, key="geocode_pick")
            sel_idx = labels.index(sel)
            sel_r = res[sel_idx]
            CENTER_LAT = float(sel_r["lat"])
            CENTER_LON = float(sel_r["lon"])
            ZOOM = 13
            st.success(f"📍 {sel_r.get('display_name','')[:100]}")

    # ── สร้างแผนที่ ───────────────────────────────────────────────────────────
    m = folium.Map(
        location=[CENTER_LAT, CENTER_LON],
        zoom_start=ZOOM,
        control_scale=True,
    )

    # plugins
    from folium import plugins as fp

    if opt_minimap:
        fp.MiniMap(toggle_display=True, position="bottomleft").add_to(m)

    if opt_measure:
        fp.MeasureControl(
            position="topleft",
            primary_length_unit="meters",
            secondary_length_unit="kilometers",
            primary_area_unit="sqmeters",
            secondary_area_unit="sqkilometers",
        ).add_to(m)

    fp.Fullscreen(position="topleft").add_to(m)
    fp.MousePosition(position="bottomright",
                     separator=" | Lon: ", prefix="Lat: ").add_to(m)

    # ── Basemaps ──────────────────────────────────────────────────────────────
    BASEMAPS = {
        "OpenStreetMap":       ("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                                "© OpenStreetMap contributors"),
        "CartoDB Positron":    ("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                                "© CartoDB"),
        "CartoDB Dark Matter": ("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                                "© CartoDB"),
        "Stamen Terrain":      ("https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg",
                                "© Stamen Design"),
        "Stamen Toner":        ("https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.png",
                                "© Stamen Design"),
        "Esri Satellite":      ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                                "© Esri"),
    }
    for name, (url, attr) in BASEMAPS.items():
        folium.TileLayer(url, attr=attr, name=name,
                         overlay=False, control=True).add_to(m)

    # ── WMS overlays ──────────────────────────────────────────────────────────
    for layer_name, cfg in WMS_CATALOG.items():
        if layer_name == "🔧 Custom WMS":
            continue
        try:
            if cfg["type"] == "wms":
                folium.WmsTileLayer(
                    url=cfg["url"], layers=cfg["layers"],
                    fmt=cfg.get("fmt", "image/png"),
                    transparent=cfg.get("transparent", True),
                    attr=cfg["attr"], name=layer_name,
                    overlay=True, control=True, show=False,
                ).add_to(m)
            else:
                folium.TileLayer(
                    cfg["url"], attr=cfg["attr"],
                    name=layer_name, overlay=True,
                    control=True, show=False,
                ).add_to(m)
        except Exception:
            pass

    # Custom WMS
    if "🔧 Custom WMS" in WMS_CATALOG and custom_url and custom_layer:
        cfg = WMS_CATALOG["🔧 Custom WMS"]
        try:
            folium.WmsTileLayer(
                url=cfg["url"], layers=cfg["layers"],
                fmt="image/png", transparent=True,
                attr=cfg["attr"], name="🔧 Custom WMS",
                overlay=True, control=True,
            ).add_to(m)
        except Exception as e:
            st.warning(f"⚠️ Custom WMS โหลดไม่ได้: {e}")

    # ── Shapefile/GeoJSON layer ───────────────────────────────────────────────
    if "gdf_loaded" in st.session_state and st.session_state.gdf_loaded is not None:
        gdf = st.session_state.gdf_loaded
        attr_cols = [c for c in gdf.columns if c != "geometry"]

        def _style_fn(x):
            return {"fillColor": "#7A2020", "color": "#7A2020",
                    "weight": 2, "fillOpacity": 0.3}

        tooltip_fields = attr_cols[:5] if attr_cols else None
        popup_fields   = attr_cols if opt_fullattr else attr_cols[:5]

        gj = folium.GeoJson(
            gdf.__geo_interface__,
            name="📂 Shapefile/GeoJSON",
            style_function=_style_fn,
            tooltip=folium.GeoJsonTooltip(
                fields=tooltip_fields,
                aliases=[f"{c}:" for c in tooltip_fields],
                sticky=True,
            ) if tooltip_fields else None,
            popup=folium.GeoJsonPopup(
                fields=popup_fields,
                aliases=[f"<b>{c}</b>" for c in popup_fields],
                max_width=400,
            ) if popup_fields else None,
        )
        gj.add_to(m)
        st.info(f"✅ Layer จากแท็บ Shapefile/GeoJSON ({len(gdf):,} features) ถูกเพิ่มบนแผนที่")

    # ── CSV points layer (with clustering) ───────────────────────────────────
    if "csv_gdf" in st.session_state and st.session_state.csv_gdf is not None:
        csv_gdf = st.session_state.csv_gdf
        attr_cols_csv = [c for c in csv_gdf.columns if c != "geometry"]

        if opt_cluster:
            marker_cluster = fp.MarkerCluster(name="📍 CSV Points (clustered)")
            for _, row in csv_gdf.iterrows():
                lat, lon = row.geometry.y, row.geometry.x
                if opt_fullattr:
                    popup_html = "<table style='font-size:12px'>"
                    for col in attr_cols_csv:
                        popup_html += f"<tr><td><b>{col}</b></td><td>{row[col]}</td></tr>"
                    popup_html += "</table>"
                else:
                    vals = {c: row[c] for c in attr_cols_csv[:4]}
                    popup_html = "<br>".join(f"<b>{k}</b>: {v}" for k, v in vals.items())

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=7, color="#7A2020",
                    fill=True, fill_color="#7A2020", fill_opacity=0.8,
                    tooltip=str(row[attr_cols_csv[0]]) if attr_cols_csv else f"{lat:.4f},{lon:.4f}",
                    popup=folium.Popup(popup_html, max_width=380),
                ).add_to(marker_cluster)
            marker_cluster.add_to(m)
        else:
            fg = folium.FeatureGroup(name="📍 CSV Points")
            for _, row in csv_gdf.iterrows():
                lat, lon = row.geometry.y, row.geometry.x
                popup_html = "<table style='font-size:12px'>"
                for col in (attr_cols_csv if opt_fullattr else attr_cols_csv[:4]):
                    popup_html += f"<tr><td><b>{col}</b></td><td>{row[col]}</td></tr>"
                popup_html += "</table>"
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=7, color="#7A2020",
                    fill=True, fill_color="#7A2020", fill_opacity=0.8,
                    tooltip=str(row[attr_cols_csv[0]]) if attr_cols_csv else "",
                    popup=folium.Popup(popup_html, max_width=380),
                ).add_to(fg)
            fg.add_to(m)
        st.info(f"✅ CSV Points ({len(csv_gdf):,} จุด) ถูกเพิ่มบนแผนที่")

    # Search result marker
    if "geocode_results" in st.session_state:
        res_list = st.session_state["geocode_results"]
        if res_list:
            r0 = res_list[st.session_state.get("geocode_selected", 0)]
            folium.Marker(
                [float(r0["lat"]), float(r0["lon"])],
                popup=r0.get("display_name", "")[:200],
                tooltip="📍 ตำแหน่งที่ค้นหา",
                icon=folium.Icon(color="red", icon="star", prefix="fa"),
            ).add_to(m)

    folium.LayerControl(collapsed=False, position="topright").add_to(m)

    map_out = st_folium(m, use_container_width=True, height=600,
                        returned_objects=["last_clicked","last_object_clicked_popup"])

    # แสดงข้อมูล popup ที่คลิก ด้านล่างแผนที่
    if map_out and map_out.get("last_clicked"):
        lc = map_out["last_clicked"]
        st.caption(f"📍 คลิกที่: Lat {lc['lat']:.6f}, Lon {lc['lng']:.6f}")

    if map_out and map_out.get("last_object_clicked_popup"):
        with st.expander("📋 ข้อมูล Feature ที่คลิก", expanded=True):
            st.markdown(map_out["last_object_clicked_popup"], unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Shapefile / GeoJSON
# ═══════════════════════════════════════════════════════════════════════════════
with tab_shape:
    st.subheader("📂 นำเข้า Shapefile / GeoJSON")

    file_type = st.radio("ประเภทไฟล์", ["GeoJSON", "Shapefile (.zip)"], horizontal=True)

    if file_type == "GeoJSON":
        geo_file = st.file_uploader("อัปโหลด GeoJSON", type=["geojson", "json"], key="geojson_up")
        if geo_file:
            try:
                gdf = gpd.read_file(geo_file)
                st.session_state.gdf_loaded = gdf
                st.success(f"✅ โหลดสำเร็จ: {len(gdf):,} features · CRS: {gdf.crs}")
            except Exception as e:
                st.error(f"อ่านไม่ได้: {e}")
    else:
        st.info("💡 zip ไฟล์ .shp, .shx, .dbf, .prj รวมกันก่อนอัปโหลด")
        shp_file = st.file_uploader("อัปโหลด Shapefile (.zip)", type=["zip"], key="shp_up")
        if shp_file:
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    zip_path = os.path.join(tmp, "data.zip")
                    with open(zip_path, "wb") as f: f.write(shp_file.read())
                    with zipfile.ZipFile(zip_path, "r") as z: z.extractall(tmp)
                    shp_files = [f for f in os.listdir(tmp) if f.endswith(".shp")]
                    if not shp_files:
                        st.error("ไม่พบไฟล์ .shp ใน zip")
                    else:
                        gdf = gpd.read_file(os.path.join(tmp, shp_files[0]))
                        st.session_state.gdf_loaded = gdf
                        st.success(f"✅ โหลดสำเร็จ: {len(gdf):,} features · CRS: {gdf.crs}")
            except Exception as e:
                st.error(f"อ่านไม่ได้: {e}")

    if "gdf_loaded" in st.session_state and st.session_state.gdf_loaded is not None:
        gdf = st.session_state.gdf_loaded
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("**Attribute Table**")
            st.dataframe(gdf.drop(columns="geometry").head(50), use_container_width=True, hide_index=True)
        with c2:
            st.markdown("**ข้อมูลพื้นที่**")
            st.markdown(f"- Features: **{len(gdf):,}**")
            st.markdown(f"- CRS: **{gdf.crs}**")
            st.markdown(f"- Geometry type: **{gdf.geom_type.value_counts().idxmax()}**")
            st.markdown(f"- Columns: **{', '.join(gdf.columns[:-1])}**")
            if gdf.geom_type.str.contains("Polygon").any():
                try:
                    gdf_proj = gdf.to_crs(epsg=32647)
                    total_area = gdf_proj.geometry.area.sum() / 1e6
                    st.markdown(f"- พื้นที่รวม: **{total_area:,.2f} km²**")
                except: pass

        # แสดงบนแผนที่ mini
        st.markdown("**Preview บนแผนที่**")
        bounds = gdf.total_bounds
        center = [(bounds[1]+bounds[3])/2, (bounds[0]+bounds[2])/2]
        m2 = folium.Map(location=center, zoom_start=7)
        folium.GeoJson(
            gdf.__geo_interface__,
            style_function=lambda x: {
                "fillColor": "#7A2020", "color": "#621a1a",
                "weight": 2, "fillOpacity": 0.35
            }
        ).add_to(m2)
        st_folium(m2, use_container_width=True, height=400, key="shp_preview")

        # ดาวน์โหลด GeoJSON
        st.download_button(
            "⬇️ Export เป็น GeoJSON",
            gdf.to_json(),
            "export.geojson", "application/json"
        )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CSV Lat/Lon
# ═══════════════════════════════════════════════════════════════════════════════
with tab_csv:
    st.subheader("📍 Plot จุดจาก CSV (Lat/Lon)")
    csv_file = st.file_uploader("อัปโหลด CSV ที่มีคอลัมน์ Latitude/Longitude", type=["csv"], key="csv_geo")

    if csv_file:
        df_csv = pd.read_csv(csv_file)
        st.dataframe(df_csv.head(5), use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        lat_col = col1.selectbox("คอลัมน์ Latitude", df_csv.columns.tolist(), key="lat_col")
        lon_col = col2.selectbox("คอลัมน์ Longitude", df_csv.columns.tolist(), key="lon_col")
        label_col = st.selectbox("คอลัมน์ Label (popup)", ["(ไม่มี)"] + df_csv.columns.tolist(), key="label_col")

        if st.button("📍 Plot บนแผนที่", type="primary"):
            try:
                df_clean = df_csv.dropna(subset=[lat_col, lon_col])
                gdf_csv = gpd.GeoDataFrame(
                    df_clean,
                    geometry=gpd.points_from_xy(df_clean[lon_col], df_clean[lat_col]),
                    crs="EPSG:4326"
                )
                st.session_state.csv_gdf = gdf_csv

                m3 = folium.Map(
                    location=[df_clean[lat_col].mean(), df_clean[lon_col].mean()],
                    zoom_start=8
                )
                for _, row in df_clean.iterrows():
                    popup_text = str(row[label_col]) if label_col != "(ไม่มี)" else ""
                    folium.CircleMarker(
                        location=[row[lat_col], row[lon_col]],
                        radius=7, color="#7A2020", fill=True,
                        fill_color="#7A2020", fill_opacity=0.7,
                        popup=popup_text
                    ).add_to(m3)

                st.success(f"✅ Plot {len(df_clean):,} จุด")
                st_folium(m3, use_container_width=True, height=500, key="csv_map")
            except Exception as e:
                st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Choropleth Map
# ═══════════════════════════════════════════════════════════════════════════════
with tab_choropleth:
    st.subheader("🎨 Choropleth Map")
    st.info("ต้องมี Shapefile/GeoJSON (แท็บที่ 2) และ CSV ข้อมูลที่ต้องการ join")

    choro_csv = st.file_uploader("อัปโหลด CSV ข้อมูล", type=["csv"], key="choro_csv")

    if "gdf_loaded" not in st.session_state or st.session_state.gdf_loaded is None:
        st.warning("⚠️ กรุณาอัปโหลด Shapefile/GeoJSON ในแท็บที่ 2 ก่อน")
    elif choro_csv:
        gdf = st.session_state.gdf_loaded
        df_choro = pd.read_csv(choro_csv)
        st.dataframe(df_choro.head(3), use_container_width=True, hide_index=True)

        c1, c2, c3 = st.columns(3)
        shp_key  = c1.selectbox("Key จาก Shapefile", gdf.columns[:-1].tolist(), key="shp_key")
        csv_key  = c2.selectbox("Key จาก CSV", df_choro.columns.tolist(), key="csv_key")
        value_col = c3.selectbox("คอลัมน์ค่า (สี)", df_choro.select_dtypes(include='number').columns.tolist(), key="choro_val")

        color_scheme = st.selectbox("Color Scheme", [
            "YlOrRd", "YlGn", "BuPu", "RdYlGn", "Blues", "Reds", "Greens"
        ], key="color_scheme")

        if st.button("🎨 สร้าง Choropleth", type="primary"):
            try:
                gdf_merged = gdf.merge(df_choro, left_on=shp_key, right_on=csv_key, how="left")
                bounds = gdf_merged.total_bounds
                center = [(bounds[1]+bounds[3])/2, (bounds[0]+bounds[2])/2]
                m4 = folium.Map(location=center, zoom_start=7)

                folium.Choropleth(
                    geo_data=gdf_merged.__geo_interface__,
                    data=gdf_merged,
                    columns=[shp_key, value_col],
                    key_on=f"feature.properties.{shp_key}",
                    fill_color=color_scheme,
                    fill_opacity=0.7,
                    line_opacity=0.5,
                    legend_name=value_col,
                    nan_fill_color="lightgray",
                ).add_to(m4)

                folium.GeoJson(
                    gdf_merged.__geo_interface__,
                    tooltip=folium.GeoJsonTooltip(
                        fields=[shp_key, value_col],
                        aliases=["พื้นที่:", f"{value_col}:"]
                    ),
                    style_function=lambda x: {"fillOpacity": 0, "weight": 0.5}
                ).add_to(m4)

                st.success("✅ สร้าง Choropleth สำเร็จ")
                st_folium(m4, use_container_width=True, height=550, key="choro_map")
            except Exception as e:
                st.error(f"Error: {e}")

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
# TAB 6 — Geoprocessing
# ═══════════════════════════════════════════════════════════════════════════════
with tab_geo:
    st.subheader("🔧 Geoprocessing")

    if "gdf_loaded" not in st.session_state or st.session_state.gdf_loaded is None:
        st.warning("⚠️ กรุณาอัปโหลด Shapefile/GeoJSON ในแท็บที่ 2 ก่อน")
    else:
        gdf = st.session_state.gdf_loaded
        st.success(f"✅ ใช้ layer: {len(gdf):,} features")

        op = st.selectbox("เลือกการประมวลผล", [
            "📐 คำนวณพื้นที่ (Area)",
            "📏 คำนวณขอบเขต (Perimeter/Length)",
            "🔵 Buffer",
            "🔗 Dissolve",
            "📦 Bounding Box",
            "🗜️ Simplify",
            "🔄 Reproject (เปลี่ยน CRS)",
        ], key="geo_op")

        result_gdf = None

        if op == "📐 คำนวณพื้นที่ (Area)":
            try:
                gdf_proj = gdf.to_crs(epsg=32647)
                gdf_out = gdf.drop(columns="geometry").copy()
                gdf_out["area_m2"]  = gdf_proj.geometry.area.round(2)
                gdf_out["area_km2"] = (gdf_proj.geometry.area / 1e6).round(4)
                gdf_out["area_rai"] = (gdf_proj.geometry.area / 1600).round(2)
                st.dataframe(gdf_out, use_container_width=True, hide_index=True)
                st.download_button("⬇️ Download CSV",
                    gdf_out.to_csv(index=False, encoding="utf-8-sig"), "area.csv", "text/csv")
            except Exception as e: st.error(f"Error: {e}")

        elif op == "📏 คำนวณขอบเขต (Perimeter/Length)":
            try:
                gdf_proj = gdf.to_crs(epsg=32647)
                gdf_out = gdf.drop(columns="geometry").copy()
                gdf_out["length_m"]  = gdf_proj.geometry.length.round(2)
                gdf_out["length_km"] = (gdf_proj.geometry.length / 1000).round(4)
                st.dataframe(gdf_out, use_container_width=True, hide_index=True)
                st.download_button("⬇️ Download CSV",
                    gdf_out.to_csv(index=False, encoding="utf-8-sig"), "length.csv", "text/csv")
            except Exception as e: st.error(f"Error: {e}")

        elif op == "🔵 Buffer":
            dist_m = st.number_input("ระยะ Buffer (เมตร)", value=1000, step=100, key="buf_dist")
            if st.button("สร้าง Buffer", type="primary"):
                try:
                    gdf_proj  = gdf.to_crs(epsg=32647)
                    buf       = gdf_proj.copy()
                    buf.geometry = gdf_proj.geometry.buffer(dist_m)
                    result_gdf = buf.to_crs(epsg=4326)
                    st.session_state.gdf_loaded = result_gdf
                    st.success(f"✅ Buffer {dist_m:,}m สำเร็จ — ไปดูผลที่แท็บ แผนที่หลัก")
                    st.download_button("⬇️ Export GeoJSON",
                        result_gdf.to_json(), "buffer.geojson", "application/json")
                except Exception as e: st.error(f"Error: {e}")

        elif op == "🔗 Dissolve":
            dissolve_col = st.selectbox("Dissolve by", ["(รวมทั้งหมด)"] + gdf.columns[:-1].tolist(), key="dis_col")
            if st.button("Dissolve", type="primary"):
                try:
                    if dissolve_col == "(รวมทั้งหมด)":
                        result_gdf = gpd.GeoDataFrame(geometry=[gdf.geometry.unary_union], crs=gdf.crs)
                    else:
                        result_gdf = gdf.dissolve(by=dissolve_col).reset_index()
                    st.session_state.gdf_loaded = result_gdf
                    st.success(f"✅ Dissolve สำเร็จ → {len(result_gdf):,} features")
                    st.download_button("⬇️ Export GeoJSON",
                        result_gdf.to_json(), "dissolved.geojson", "application/json")
                except Exception as e: st.error(f"Error: {e}")

        elif op == "📦 Bounding Box":
            try:
                bounds = gdf.total_bounds
                st.markdown(f"""
**Bounding Box:**
- Min Lon (West): `{bounds[0]:.6f}`
- Min Lat (South): `{bounds[1]:.6f}`
- Max Lon (East): `{bounds[2]:.6f}`
- Max Lat (North): `{bounds[3]:.6f}`
""")
                from shapely.geometry import box as shapely_box
                bbox_gdf = gpd.GeoDataFrame(geometry=[shapely_box(*bounds)], crs=gdf.crs)
                st.download_button("⬇️ Export Bounding Box GeoJSON",
                    bbox_gdf.to_json(), "bbox.geojson", "application/json")
            except Exception as e: st.error(f"Error: {e}")

        elif op == "🗜️ Simplify":
            tol = st.number_input("Tolerance (degree)", value=0.001, format="%.4f", key="simp_tol")
            if st.button("Simplify", type="primary"):
                try:
                    result_gdf = gdf.copy()
                    result_gdf.geometry = gdf.geometry.simplify(tol, preserve_topology=True)
                    st.session_state.gdf_loaded = result_gdf
                    st.success(f"✅ Simplify สำเร็จ")
                    st.download_button("⬇️ Export GeoJSON",
                        result_gdf.to_json(), "simplified.geojson", "application/json")
                except Exception as e: st.error(f"Error: {e}")

        elif op == "🔄 Reproject (เปลี่ยน CRS)":
            epsg_target = st.number_input("EPSG Code เป้าหมาย", value=32647, step=1, key="epsg_target")
            st.caption("ตัวอย่าง: 4326=WGS84, 32647=UTM47N (ไทย), 32648=UTM48N")
            if st.button("Reproject", type="primary"):
                try:
                    result_gdf = gdf.to_crs(epsg=int(epsg_target))
                    st.session_state.gdf_loaded = result_gdf
                    st.success(f"✅ Reproject เป็น EPSG:{epsg_target} สำเร็จ")
                    st.download_button("⬇️ Export GeoJSON",
                        result_gdf.to_crs(epsg=4326).to_json(), "reprojected.geojson", "application/json")
                except Exception as e: st.error(f"Error: {e}")

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
            df_pk = df_pk.rename(columns={pk_lat: "lat", pk_lon: "lon"})
            df_pk = df_pk.dropna(subset=["lat","lon"])

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

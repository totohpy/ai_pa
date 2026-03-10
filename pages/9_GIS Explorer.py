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
tab_map, tab_shape, tab_csv, tab_choropleth, tab_heatmap, tab_geo = st.tabs([
    "🗺️ แผนที่หลัก",
    "📂 Shapefile / GeoJSON",
    "📍 CSV Lat/Lon",
    "🎨 Choropleth Map",
    "🌡️ Heatmap",
    "🔧 Geoprocessing",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — แผนที่หลัก
# ═══════════════════════════════════════════════════════════════════════════════
with tab_map:
    st.subheader("🗺️ แผนที่ Interactive")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        center_lat = st.number_input("Latitude ศูนย์กลาง", value=13.7563, format="%.4f", key="c_lat")
    with col2:
        center_lon = st.number_input("Longitude ศูนย์กลาง", value=100.5018, format="%.4f", key="c_lon")
    with col3:
        zoom = st.slider("Zoom", 1, 18, 6, key="map_zoom")
    with col4:
        basemap = st.selectbox("Basemap", [
            "OpenStreetMap",
            "CartoDB positron",
            "CartoDB dark_matter",
            "Stamen Terrain",
            "Stamen Toner",
            "Esri WorldImagery",
        ], key="basemap_sel")

    # ── WMS/WMTS Layer Selector ───────────────────────────────────────────────
    WMS_CATALOG = {
        "🇹🇭 RTSD Orthophoto (กรมแผนที่ทหาร)": {
            "type": "wms",
            "url": "https://geoportal.rtsd.mi.th/arcgis/services/FGDS/Orthophoto/ImageServer/WMSServer",
            "layers": "0", "attr": "© กรมแผนที่ทหาร RTSD",
            "fmt": "image/png", "transparent": True,
        },
        "🇹🇭 RTSD แผนที่ฐาน (กรมแผนที่ทหาร)": {
            "type": "wms",
            "url": "https://geoportal.rtsd.mi.th/arcgis/services/FGDS/Base_Map/MapServer/WMSServer",
            "layers": "0", "attr": "© กรมแผนที่ทหาร RTSD",
            "fmt": "image/png", "transparent": True,
        },
        "🇹🇭 NSO สถิติ (สำนักงานสถิติแห่งชาติ)": {
            "type": "wms",
            "url": "https://gis.nso.go.th/geoserver/wms",
            "layers": "nso:province", "attr": "© NSO Thailand",
            "fmt": "image/png", "transparent": True,
        },
        "🌍 NASA GIBS MODIS Terra (ดาวเทียมรายวัน)": {
            "type": "tile",
            "url": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2024-01-01/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
            "attr": "© NASA GIBS",
        },
        "🌍 NASA GIBS VIIRS Night Lights": {
            "type": "tile",
            "url": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_DayNightBand_ENCC/default/2024-01-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.png",
            "attr": "© NASA GIBS VIIRS",
        },
        "🌍 OpenTopoMap (ภูมิประเทศ)": {
            "type": "tile",
            "url": "https://tile.opentopomap.org/{z}/{x}/{y}.png",
            "attr": "© OpenTopoMap contributors",
        },
        "🌍 Esri World Shaded Relief": {
            "type": "tile",
            "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}",
            "attr": "© Esri",
        },
        "🌍 Esri World Street Map": {
            "type": "tile",
            "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
            "attr": "© Esri",
        },
    }

    with st.expander("🛰️ เพิ่ม WMS/WMTS Overlay Layers", expanded=False):
        col_wms1, col_wms2 = st.columns([3,1])
        with col_wms1:
            selected_wms = st.multiselect(
                "เลือก Layer ที่ต้องการซ้อนทับ (เลือกได้หลาย layer)",
                list(WMS_CATALOG.keys()),
                key="wms_selected",
            )
        with col_wms2:
            wms_opacity = st.slider("Opacity", 0.1, 1.0, 0.8, 0.1, key="wms_opacity")

        with st.expander("➕ เพิ่ม WMS URL เอง"):
            cw1, cw2 = st.columns(2)
            custom_url   = cw1.text_input("WMS URL", key="custom_wms_url",
                placeholder="https://example.com/geoserver/wms")
            custom_layer = cw2.text_input("Layer Name", key="custom_wms_layer",
                placeholder="workspace:layername")
            custom_attr  = st.text_input("Attribution", value="Custom WMS", key="custom_wms_attr")
            if custom_url and custom_layer:
                WMS_CATALOG["🔧 Custom WMS"] = {
                    "type": "wms", "url": custom_url, "layers": custom_layer,
                    "attr": custom_attr, "fmt": "image/png", "transparent": True,
                }
                if "🔧 Custom WMS" not in selected_wms:
                    selected_wms = list(selected_wms) + ["🔧 Custom WMS"]

    TILE_URLS = {
        "OpenStreetMap":      ("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                               "© OpenStreetMap contributors"),
        "CartoDB positron":   ("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                               "© CartoDB"),
        "CartoDB dark_matter":("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                               "© CartoDB"),
        "Stamen Terrain":     ("https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg",
                               "© Stamen Design"),
        "Stamen Toner":       ("https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.png",
                               "© Stamen Design"),
        "Esri WorldImagery":  ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                               "© Esri"),
    }

    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom)
    tile_url, attr = TILE_URLS.get(basemap, TILE_URLS["OpenStreetMap"])
    if basemap != "OpenStreetMap":
        folium.TileLayer(tile_url, attr=attr, name=basemap).add_to(m)

    # inject WMS/Tile overlay layers
    for layer_name in (selected_wms or []):
        cfg = WMS_CATALOG.get(layer_name)
        if not cfg: continue
        try:
            if cfg["type"] == "wms":
                folium.WmsTileLayer(
                    url=cfg["url"], layers=cfg["layers"],
                    fmt=cfg.get("fmt","image/png"),
                    transparent=cfg.get("transparent", True),
                    attr=cfg["attr"], name=layer_name,
                    overlay=True, control=True,
                    opacity=wms_opacity,
                ).add_to(m)
            else:
                folium.TileLayer(
                    cfg["url"], attr=cfg["attr"],
                    name=layer_name, overlay=True, control=True,
                    opacity=wms_opacity,
                ).add_to(m)
        except Exception as e:
            st.warning(f"⚠️ โหลด layer ไม่ได้ [{layer_name}]: {e}")

    folium.LayerControl(collapsed=False).add_to(m)

    # แสดง layers ที่ upload ไว้ (จาก session_state)
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

    st_folium(m, use_container_width=True, height=550)

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

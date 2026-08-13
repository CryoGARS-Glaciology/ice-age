import folium
import streamlit as st
from shapely.geometry import box
from streamlit_folium import st_folium

from database import MELT_RATES_TABLE, SHAPE_TABLE
from modules.map_backgrounds import MAP_BACKGROUNDS
from modules.plotting import attach_highlight_script, iceberg_map
from modules.shape_viewer import map_data, shape_dates_for_site
from modules.ui_elements import (
    GLACIER_ID_KEY,
    date_range_selector,
    has_records,
    site_and_date_query_params,
    site_name_selector,
    statistics_button,
)

selected_site, selected_dates = site_and_date_query_params()

st.title("Iceberg Viewer")

with st.container():
    col1, col2 = st.columns(2, vertical_alignment="bottom")
    with col1:
        st.header("Filter")
    with col2:
        with st.container(horizontal_alignment="right"):
            if selected_site and has_records(MELT_RATES_TABLE, selected_site):
                statistics_button(
                    selected_site, selected_dates, full_width=False, type="primary"
                )

    menu_col_1, menu_col_2 = st.columns(2)

with menu_col_1:
    site_select = site_name_selector(SHAPE_TABLE, selected_site)

if site_select:
    with menu_col_2:
        available_dates = shape_dates_for_site(site_select[GLACIER_ID_KEY])
        date_range = date_range_selector(available_dates, selected_dates)

if site_select:
    st.header("Map")
    st.caption(
        "Lines connect an iceberg's repeat observations only within a single "
        "imagery campaign. Iceberg ID numbers are reused across different "
        "campaigns/years for unrelated icebergs, so observations from "
        "different campaigns are never connected, even if shown in the same "
        "color."
    )

    glacier_sites = map_data(site_select, date_range)
    features, iceberg_sites = iceberg_map(glacier_sites)

    map_center = box(*iceberg_sites.total_bounds).centroid
    esri = MAP_BACKGROUNDS["ESRI"]
    map_element = folium.Map(location=[map_center.y, map_center.x], tiles=None)
    # Muted opacity on the satellite basemap so the iceberg overlays (drawn at
    # full opacity) read as the clear focal layer, not the imagery.
    folium.TileLayer(
        tiles=esri["tiles"], attr=esri["attribution"], opacity=0.6,
    ).add_to(map_element)
    # Dedicated pane above the default overlay pane, so the arrowheads added to
    # the feature group always render on top of the iceberg polygons regardless
    # of layer add order.
    folium.map.CustomPane("arrowheads", z_index=650).add_to(map_element)
    # Frame the actual extent of the icebergs shown rather than a fixed zoom
    # level: a fixed zoom either clips widely-scattered icebergs or leaves a
    # tight cluster zoomed too far out.
    minx, miny, maxx, maxy = iceberg_sites.total_bounds
    map_element.fit_bounds([[miny, minx], [maxy, maxx]])
    attach_highlight_script(map_element)

    st_folium(
        map_element,
        # Features are handed to st_folium separately rather than baked into
        # the map, so changing the observation period swaps the shapes instead
        # of tearing down and rebuilding the whole map.
        feature_group_to_add=features,
        center=(map_center.y, map_center.x),
        use_container_width=True,
        height=480,
        returned_objects=None,
        key="Iceberg-Viewer-Map",
    )

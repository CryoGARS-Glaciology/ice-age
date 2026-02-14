import streamlit as st
from streamlit_folium import st_folium

from database import SHAPE_TABLE
from modules.database import get_table
from modules.plotting import iceberg_map
from modules.shape_viewer import map_data
from modules.ui_elements import (
    DATE_PARAM,
    SITE_PARAM,
    date_range_selector,
    site_name_selector,
)

st.title("Iceberg Viewer")

SHAPES = get_table(SHAPE_TABLE)
query_params = st.query_params
selected_site = query_params.get(SITE_PARAM, None)
selected_dates = query_params.get(DATE_PARAM, None)

with st.container():
    st.header("Filter")
    menu_col_1, menu_col_2 = st.columns(2)

with menu_col_1:
    site_select = site_name_selector(SHAPES, selected_site)

if site_select:
    with menu_col_2:
        date_range = date_range_selector(site_select, selected_dates)

if site_select:
    st.header("Map")
    glacier_sites = map_data(site_select, date_range)
    map_object = iceberg_map(glacier_sites)

    st_folium(map_object, use_container_width=True, returned_objects=None)

import streamlit as st
from streamlit_folium import st_folium

from database import SHAPE_TABLE
from modules.database import db_table
from modules.plotting import iceberg_map
from modules.shape_viewer import map_data
from modules.statistics import statistic_dates_for_site
from modules.ui_elements import (
    GLACIER_ID_KEY,
    date_range_selector,
    site_and_date_query_params,
    site_name_selector,
)

selected_site, selected_dates = site_and_date_query_params()

st.title("Iceberg Viewer")

with st.container():
    st.header("Filter")
    menu_col_1, menu_col_2 = st.columns(2)

with menu_col_1:
    site_select = site_name_selector(db_table(SHAPE_TABLE), selected_site)

if site_select:
    with menu_col_2:
        available_dates = statistic_dates_for_site(site_select[GLACIER_ID_KEY])
        date_range = date_range_selector(available_dates, selected_dates)

if site_select:
    st.header("Map")
    glacier_sites = map_data(site_select, date_range)
    map_object = iceberg_map(glacier_sites)

    st_folium(map_object, use_container_width=True, returned_objects=None)

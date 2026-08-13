import streamlit as st
from streamlit_folium import st_folium

from database import MELT_RATES_TABLE, SHAPE_TABLE
from modules.database import db_table
from modules.plotting import iceberg_map
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
    site_select = site_name_selector(db_table(SHAPE_TABLE), selected_site)

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
    map_object = iceberg_map(glacier_sites)

    st_folium(map_object, use_container_width=True, height=480, returned_objects=None)

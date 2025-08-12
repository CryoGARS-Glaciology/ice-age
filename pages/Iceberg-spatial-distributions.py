import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import os

from modules.data_path import GLACIER_LOCATIONS_CSV, SHAPEFILE_CATALOG_DIR
from modules.plotting import iceberg_map, get_available_dates

# Title and description
st.title("🗺️ Visualize iceberg spatial distributions")
st.markdown("This interactive map allows you to zoom into specific sites and visualize iceberg distributions in Greenland.")
st.info('Click here for the [Fjord Abbreviation List & Paired Dates](https://docs.google.com/spreadsheets/d/1kCcKqf717kK3_Xx-GDe0f61jhlUpZ5n6BN1qtiw7S4w/edit?gid=0#gid=0)')

glacier_sites = pd.read_csv(GLACIER_LOCATIONS_CSV)

# User filter top row
with st.container():
    st.header("Filter")
    menu_col_1_1, menu_col_1_2, menu_col_1_3 = st.columns(3)

with menu_col_1_1:
    # Sidebar: Select site ID
    site_id = st.selectbox(
        "Select a Glacier site: ",
        sorted(glacier_sites["Glacier_ID"].unique()),
        index=sorted(glacier_sites["Glacier_ID"].unique()).index("NOG"),
    )
with menu_col_1_2:
    early_date = st.text_input("Enter Early Date (YYYYMMDD):", "20170515")  #Default date
with menu_col_1_3:
    later_date = st.text_input("Enter Later Date (YYYYMMDD):", "20170611")

# User filter second row
with st.container():
    st.header("Visualize")
    menu_col_2_1, menu_col_2_2, menu_col_2_3 = st.columns(3)

# Sidebar: Get available date ranges for the selected site
available_dates = get_available_dates(site_id)

if available_dates:
    with menu_col_2_1:
        selected_date_range = st.selectbox("Select Date Range", available_dates)
    early_date, later_date = selected_date_range.split('-')
else:
    st.error(f"No available date ranges found for site: {site_id}")
    early_date, later_date = "", ""

# Sidebar: Select icebergs for map
shapefile_dir = os.path.join(SHAPEFILE_CATALOG_DIR, site_id, f"{early_date}-{later_date}")
shapefiles = [
    f for f in os.listdir(shapefile_dir) if f.endswith(".shp")
] if os.path.exists(shapefile_dir) else []

# Select specific icebergs
with menu_col_2_2:
    plot_option = st.radio("Plot icebergs:", ("Plot selected date range", "Select specific icebergs"))
    selected_icebergs = st.multiselect("Select Icebergs to View", shapefiles, default=shapefiles[:1]) if plot_option == "Select specific icebergs" else shapefiles
with menu_col_2_3:
    st.markdown("👆Click the icebergs to view their width, height, and more details!")
    st.markdown("✋ Pan around the map to see how icebergs drift!")
    st.markdown("🔎 Zoom out to see the full extent!")

# Generate and display map
if selected_icebergs:
    map_object = iceberg_map(
        glacier_sites,
        site_id,
        early_date,
        later_date,
    )
    st_folium(map_object, width=800, height=600)
    
else:
    st.write("")

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import os

st.markdown(
    """
    <style>
    /* Title text color */
    .stTitle {
        color: #000000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title and description
st.title("🗺️ Visualize iceberg spatial distributions")
st.markdown("This interactive map allows you to zoom into specific sites and visualize iceberg distributions in Greenland.")

# Sidebar image and informational links
st.sidebar.image(
    "catalog-data/images/Glacier-iceberg.png",
    caption="Iceberg in Kongsfjord, Svalbard. Credit: Allen Pope, NSIDC"
)
st.sidebar.markdown('Fill out the prompts below to display the interactive map!')
st.markdown('👆Click the icebergs to view their width, height, and more details!')
st.markdown('✋ Pan around the map to see how icebergs drift!')
st.markdown('🔎 Zoom out to see the full extent!')

# Sidebar for Fjord Abbreviation List & Paired Dates
st.info('Click here for the [Fjord Abbreviation List & Paired Dates](https://docs.google.com/spreadsheets/d/1kCcKqf717kK3_Xx-GDe0f61jhlUpZ5n6BN1qtiw7S4w/edit?gid=0#gid=0)')

# File paths
csv_file_path = "catalog-data/Glacier-Locations.csv"
shapefile_base_path = "catalog-data/iceberg-shapefiles"

# Function to load and reproject shapefile
def load_and_reproject_shapefile(filepath):
    gdf = gpd.read_file(filepath)
    if gdf.crs is None:
        gdf.set_crs("EPSG:3413", inplace=True)
    return gdf.to_crs("EPSG:4326")

# Function to calculate width and height of iceberg
def calculate_width_height(gdf):
    # Reproject to EPSG:3413 (meters)
    gdf = gdf.to_crs("EPSG:3413")

    # Get the bounding box of the iceberg shape in meters
    bounds = gdf.total_bounds
    width = bounds[2] - bounds[0]  # x_max - x_min (in meters)
    height = bounds[3] - bounds[1]  # y_max - y_min (in meters)

    # Return width and height rounded to 2 decimal places
    return round(width, 2), round(height, 2)

# Function to get available date ranges based on site ID
def get_available_dates(site_id):
    site_path = os.path.join(shapefile_base_path, site_id)
    if os.path.exists(site_path):
        return [f for f in os.listdir(site_path) if os.path.isdir(os.path.join(site_path, f))]
    return []

# Function to create the interactive map with icebergs
def create_interactive_map(glacier_sites, site_id, early_date, later_date, selected_icebergs):
    site = glacier_sites[glacier_sites['Glacier_ID'] == site_id]
    site_lat, site_lon = site.iloc[0]['LAT'], site.iloc[0]['LON']

    # Initialize map
    m = folium.Map(location=[site_lat, site_lon], zoom_start=12.3, tiles="CartoDB positron")

    # Define color mapping for dates
    date_colors = {
        early_date: "blue",
        later_date: "green"
    }

    # Add iceberg shapefiles to the map
    site_path = os.path.join(shapefile_base_path, site_id, f"{early_date}-{later_date}")
    if os.path.exists(site_path):
        shapefiles = [f for f in os.listdir(site_path) if f.endswith(".shp")]
        for iceberg in shapefiles:
            shp_path = os.path.join(site_path, iceberg)
            gdf = load_and_reproject_shapefile(shp_path)

            # Calculate width and height
            width, height = calculate_width_height(gdf)

            color = "#7a1037" if early_date in iceberg else "#033b59" if later_date in iceberg else "gray"
            popup_content = f"<strong>Iceberg ID:</strong> {iceberg}<br><strong>Width:</strong> {width} meters<br><strong>Height:</strong> {height} meters"

            # Add GeoJson to map with popups
            folium.GeoJson(
                gdf.__geo_interface__,
                name=iceberg,
                style_function=lambda x, color=color: {"color": color, "weight": 1},
                popup=folium.Popup(popup_content, max_width=300)
            ).add_to(m)

            # Zoom into iceberg centroid
            centroid = gdf.geometry.centroid.iloc[0]
            m.location = [centroid.y, centroid.x]
            m.zoom_start = 12

    return m

# Read glacier sites and process user input
try:
    glacier_sites = pd.read_csv(csv_file_path)

    # Sidebar: Select site ID
    #site_id = st.sidebar.selectbox("Select Glacier Site", sorted(glacier_sites['Glacier_ID'].unique()))
    site_id = st.sidebar.selectbox("Select a Glacier site: ", sorted(glacier_sites['Glacier_ID'].unique()), index = sorted(glacier_sites['Glacier_ID'].unique()).index("NOG"))
    # Sidebar: Get available date ranges for the selected site
    available_dates = get_available_dates(site_id)

    if available_dates:
        selected_date_range = st.sidebar.selectbox("Select Date Range", available_dates)
        early_date, later_date = selected_date_range.split('-')
    else:
        st.error(f"No available date ranges found for site: {site_id}")
        early_date, later_date = "", ""

    # Sidebar: Select icebergs for map
    shapefile_dir = os.path.join(shapefile_base_path, site_id, f"{early_date}-{later_date}")
    shapefiles = [f for f in os.listdir(shapefile_dir) if f.endswith(".shp")] if os.path.exists(shapefile_dir) else []

    plot_option = st.sidebar.radio("Plot icebergs:", ("Plot selected date range", "Select specific icebergs"))

    # Select specific icebergs
    selected_icebergs = st.multiselect("Select Icebergs to View", shapefiles, default=shapefiles[:1]) if plot_option == "Select specific icebergs" else shapefiles

    # Generate and display map
    if selected_icebergs:
        map_object = create_interactive_map(glacier_sites, site_id, early_date, later_date, selected_icebergs)
        st_folium(map_object, width=800, height=600)
    else:
        st.write("")

except Exception as e:
    st.error(f"An error occurred: {e}")




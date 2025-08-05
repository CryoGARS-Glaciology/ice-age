import folium
import geopandas as gpd
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.html(
    '''
    <h1 style="
        font-family: 'Bungee Shade', 'Audiowide', sans-serif;
        font-size: 40px;
        text-align: center;
        background: linear-gradient(90deg, #9c27b0, #e91e63, #ff5722, #ffeb3b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;">
        ICE-AGE Innovation: Empowering Iceberg Analysis in Greenland Environments
    </h1>
    ''',
)

# Brief description of the app
st.text(
    "The ICE-AGE catalog is a powerful tool for iceberg research, offering "
    "easy access to iceberg identification, metrics, and imagery."
)

# You can alter the map properties here:
map_style = st.sidebar.selectbox(
    "Select Map Style",
    options=["CartoDB positron", "CartoDB dark_matter"],
    index=0  #This line sets the default, change to 1 for dark_matter default.
)

#Define your path to data here:
csv_file_path = "catalog-data/Glacier-Locations.csv"
natural_earth_path = "catalog-data/ne_110m_admin_0_countries.zip"
histo_csv_file_path = "catalog-data/abbreviations-datepairings.csv"

#Function for the interactive map:
def create_interactive_map(glacier_sites, map_style):
    # Load Natural Earth dataset
    world = gpd.read_file(natural_earth_path)
    greenland = world[world['NAME'] == 'Greenland']

    # This will convert Greenland to GeoJSON for Folium package:
    greenland_geojson = greenland.to_crs("EPSG:4326").__geo_interface__
    m = folium.Map(location=[72, -40], zoom_start=4, tiles=map_style)

    # Main Greenland shapefile customization:
    folium.GeoJson(
        greenland_geojson,
        name="Greenland",
        style_function=lambda x: {"fillColor": "#3156de", "color": "black", "weight": 1.0},
    ).add_to(m)

    # Sorts sites into regional categories:
    region_colors = {
        'SE': 'red',
        'CE': 'orange',
        'CW': 'yellow',
        'NW': 'green',
        'NE': 'lime',
        'NO': 'blue',
        'SW': 'purple'
    }

    # Add markers to signify study sites:
    for _, site in glacier_sites.iterrows():
        region = site['Region']
        color = region_colors.get(region, 'red')

        folium.Marker(
            location=[site['LAT'], site['LON']],
            popup=f"Official Name: {site['Official_n']}",
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(m)

    return m

# Create the map with interactive controls in an expandable section
with st.expander("🗺️ Map of Greenland with selected study sites", expanded=True):
    try:
        glacier_sites = pd.read_csv(csv_file_path)
        required_columns = {'LAT', 'LON', 'Official_n', 'Glacier_ID', 'Region'}
        if not required_columns.issubset(glacier_sites.columns):
            st.error(f"The uploaded file must contain the following columns: {', '.join(required_columns)}")
        else:
            interactive_map = create_interactive_map(glacier_sites, map_style)
            st_folium(interactive_map, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred while loading the CSV file: {e}")

st.markdown("Years represented in study: 2011 - 2023")

with st.expander("How to access ICE-AGE:", expanded=True):
    st.text(
        "ICE-AGE data will be archived at the Arctic Data Center. "
        "Code is available via GitHub, and Zenodo for future growth "
        "and automated figure generation."
    )

st.title("Contents of ICE-AGE application:")

# Individual Iceberg Metrics
with st.expander("📈 Individual Iceberg Metrics", expanded=True):
    st.html(
        """
        <div class="content-box metrics-box">
            <ul>
                <li>Location, repeat imagery metadata, and identification for iceberg studies.</li>
                <li>Access code for shapefiles to connect to ICE-AGE metrics.</li>
                <li>Iceberg size, volume, draft, and submerged area data.</li>
            </ul>
        </div>
        """,
    )

# Change Over Time Metrics
with st.expander("⏱️ Change Over Time Metrics", expanded=True):
    st.html(
        """
        <div class="content-box change-box">
            <ul>
                <li>Volume change rate and elevation change rate over time.</li>
            </ul>
        </div>
        """,
    )

# Regional Iceberg Metrics
with st.expander("🏞️ Regional Iceberg Metrics", expanded=True):
    st.html(
        """
        <div class="content-box regional-box">
            <ul>
                <li>Iceberg size distributions across time and location.</li>
            </ul>
        </div>
        """,
    )


st.info(
    "ICE-AGE will be under continuous development and growth! "
    "Some sites do not have data quite yet, so we appreciate your patience "
    "while we work on updating our datasets. The following histogram shows "
    "how much data each study site has."
)
df = pd.read_csv(histo_csv_file_path)

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Path to your CSV file (update this path if necessary)
csv_file_path = "catalog-data/abbreviations-datepairings.csv"

# Read the CSV file
df = pd.read_csv(csv_file_path)

# Check if the necessary columns exist
if 'Official_n' in df.columns and 'Corresponding icebergs' in df.columns:
    # Sort the dataframe by 'Corresponding icebergs' in ascending order
    df_sorted = df.sort_values(by='Corresponding icebergs', ascending=True)

    # Extract the names and values after sorting
    names = df_sorted['Official_n'].astype(str)  # Convert iceberg names to strings
    values = df_sorted['Corresponding icebergs'].astype(float)  # Convert iceberg values to floats for proper color scaling

    # Normalize the values to adjust the color intensity
    norm = plt.Normalize(values.min(), values.max())
    cmap = plt.cm.Blues  # Color map for blue shades

    # Create the plot
    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, values, color=cmap(norm(values)), edgecolor='black')  # Add black border and color based on values

    # Add axis labels and title
    plt.xlabel('Study site', fontsize=12)
    plt.ylabel('Corresponding Icebergs', fontsize=12)
    plt.title('Data distribution for Greenland Glacier study sites', fontsize=14)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Display the plot
    st.pyplot(plt)
else:
    st.error("The required columns ('Official_n' and 'Corresponding icebergs') are not in the CSV file.")

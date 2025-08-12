import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_folium import st_folium

from .data_path import NATURAL_EARTH_PATH, GLACIER_LOCATIONS_CSV

def distribution(csv_file):
    df = pd.read_csv(csv_file)

    df_sorted = df.sort_values(by='Corresponding icebergs', ascending=True)
    names = df_sorted['Official_n'].astype(str)
    # Convert iceberg values to floats for proper color scaling
    values = df_sorted['Corresponding icebergs'].astype(float)

    # Normalize the values to adjust the color intensity
    norm = plt.Normalize(values.min(), values.max())
    cmap = plt.cm.Blues  # Color map for blue shades

    plt.figure(figsize=(10, 6))
    plt.bar(names, values, color=cmap(norm(values)), edgecolor='black')

    plt.title('Data distribution for Greenland Glacier study sites', fontsize=14)
    plt.xlabel('Study site', fontsize=12)
    plt.ylabel('Corresponding Icebergs', fontsize=12)
    plt.xticks(rotation=45, ha='right')

    return plt

def interactive_map(map_style):
    glacier_sites = pd.read_csv(GLACIER_LOCATIONS_CSV)
    world = gpd.read_file(NATURAL_EARTH_PATH)
    greenland = world[world['NAME'] == 'Greenland']

    # This will convert Greenland to GeoJSON for Folium package:
    greenland_geojson = greenland.to_crs("EPSG:4326").__geo_interface__
    map = folium.Map(location=[72, -40], zoom_start=4, tiles=map_style)

    # Main Greenland shapefile customization:
    folium.GeoJson(
        greenland_geojson,
        name="Greenland",
        style_function=lambda x: {"fillColor": "#3156de", "color": "black", "weight": 1.0},
    ).add_to(map)

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
        ).add_to(map)

    return st_folium(map, use_container_width=True)

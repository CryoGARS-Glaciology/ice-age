import os

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.affinity import translate
from streamlit_folium import st_folium

from .data_path import (
    GLACIER_LOCATIONS_CSV,
    HISTO_CSV_FILE_PATH,
    NATURAL_EARTH_PATH,
    SHAPEFILE_CATALOG_DIR,
)


def distribution_plot():
    df = pd.read_csv(HISTO_CSV_FILE_PATH)

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

def overview_map(map_style):
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

def calculate_dominant_angle(gdf):
    """
    This function will calculate the dominant angle of the iceberg shapes, so that they
    plot a little nicer and more uniform. It will use the average dominant angle.
    """
    gdf = gdf[gdf['geometry'].is_valid]  # Ensure geometry is valid
    bounds = gdf['geometry'].apply(lambda geom: geom.minimum_rotated_rectangle)

    def longest_edge_angle(box):
        coords = np.array(box.exterior.coords)
        edges = np.diff(coords, axis=0)[:-1]
        lengths = np.linalg.norm(edges, axis=1)
        longest_idx = np.argmax(lengths)
        longest_edge = edges[longest_idx]
        angle = np.arctan2(longest_edge[1], longest_edge[0])
        return np.degrees(angle)

    angles = bounds.apply(longest_edge_angle)
    return angles.mean()

quartile_colors = {"Q1": "#8bd67a", "Q2": "#e080d7", "Q3": "#f7bf07", "Q4": "#f78307"}
quartile_opacity = {"Q1": 0.4, "Q2": 0.4, "Q3": 0.4, "Q4": 0.4}

def iceberg_quartiles(area_df, target_folder):
    # This will help with consistent scaling:
    max_width, max_height = 0, 0
    for shapefile in area_df["Shapefile"]:
        shapefile_path = os.path.join(target_folder, shapefile)
        gdf = gpd.read_file(shapefile_path)

        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:3413")
        gdf = gdf.to_crs("EPSG:3413")

        if not gdf.empty:
            bounds = gdf.total_bounds
            max_width = max(max_width, bounds[2] - bounds[0])
            max_height = max(max_height, bounds[3] - bounds[1])
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 12), sharex=True, sharey=True)
    axes = axes.flatten()

    for i, quartile in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        ax = axes[i]
        ax.set_title(f"Quartile {quartile}", fontsize=10)

        quartile_files = area_df[area_df["Quartile"] == quartile]["Shapefile"]

        for shapefile in quartile_files:
            shapefile_path = os.path.join(target_folder, shapefile)
            gdf = gpd.read_file(shapefile_path)

            if gdf.crs is None:
                gdf = gdf.set_crs(
                    "EPSG:3413"
                )  # Proper projection for Greenland; this value will change depending on where your data is!
            gdf = gdf.to_crs("EPSG:3413")

            color = quartile_colors[quartile]
            opacity = quartile_opacity[quartile]

            overall_bounds = gdf.total_bounds
            gdf["geometry"] = gdf["geometry"].apply(
                lambda geom: translate(geom, -overall_bounds[0], -overall_bounds[1])
            )

            gdf.plot(ax=ax, color=color, edgecolor="black", alpha=opacity, linewidth=2)

        ax.set_xlim(0, max_width)
        ax.set_ylim(0, max_height)
        ax.set_xlabel("Width (m)")
        ax.set_ylabel("Height (m)")

    return fig

def load_and_reproject_shapefile(filepath):
    gdf = gpd.read_file(filepath)
    if gdf.crs is None:
        gdf.set_crs("EPSG:3413", inplace=True)
    return gdf.to_crs("EPSG:4326")

def calculate_width_height(gdf):
    # Reproject to EPSG:3413 (meters)
    gdf = gdf.to_crs("EPSG:3413")

    # Get the bounding box of the iceberg shape in meters
    bounds = gdf.total_bounds
    width = bounds[2] - bounds[0]  # x_max - x_min (in meters)
    height = bounds[3] - bounds[1]  # y_max - y_min (in meters)

    # Return width and height rounded to 2 decimal places
    return round(width, 2), round(height, 2)

def get_available_dates(site_id):
    """
    Get available date ranges based on site ID
    """
    site_path = os.path.join(SHAPEFILE_CATALOG_DIR, site_id)
    if os.path.exists(site_path):
        return [f for f in os.listdir(site_path) if os.path.isdir(os.path.join(site_path, f))]
    return []

def iceberg_map(glacier_sites, site_id, early_date, later_date):
    """
    Interactive map with icebergs
    """
    site = glacier_sites[glacier_sites['Glacier_ID'] == site_id]
    site_lat, site_lon = site.iloc[0]['LAT'], site.iloc[0]['LON']

    m = folium.Map(
        location=[site_lat, site_lon],
        zoom_start=12.3,
        tiles="CartoDB positron"
    )

    # Add iceberg shapefiles to the map
    site_path = os.path.join(SHAPEFILE_CATALOG_DIR, site_id, f"{early_date}-{later_date}")
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

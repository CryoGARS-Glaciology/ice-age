import os

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

from shapely.affinity import translate
from streamlit_folium import st_folium

from database import LOCATIONS_TABLE
from modules.database import get_table

LOCATIONS = get_table(LOCATIONS_TABLE)


def overview_map(map_style):
    glacier_sites = gpd.GeoDataFrame(
        LOCATIONS.execute(), geometry="geometry", crs="EPSG:4326"
    )

    map = folium.Map(location=[72, -40], zoom_start=4, tiles=map_style)

    # Add markers to signify study sites:
    tooltip = folium.GeoJsonTooltip(
        fields=["Glacier_ID", "Official_name"],
        aliases=["ID", "Name"],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        """,
        max_width=400,
    )
    folium.GeoJson(
        glacier_sites,
        name="Iceberg Study Sites",
        zoom_on_click=True,
        marker=folium.Marker(icon=folium.Icon(icon="star")),
        tooltip=tooltip,
    ).add_to(map)

    return st_folium(map, returned_objects=[], use_container_width=True)


def calculate_dominant_angle(gdf):
    """
    This function will calculate the dominant angle of the iceberg shapes, so that they
    plot a little nicer and more uniform. It will use the average dominant angle.
    """
    gdf = gdf[gdf["geometry"].is_valid]  # Ensure geometry is valid
    bounds = gdf["geometry"].apply(lambda geom: geom.minimum_rotated_rectangle)

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
        return [
            f
            for f in os.listdir(site_path)
            if os.path.isdir(os.path.join(site_path, f))
        ]
    return []


def iceberg_map(glacier_sites, site_id, early_date, later_date):
    """
    Interactive map with icebergs
    """
    site = glacier_sites[glacier_sites["Glacier_ID"] == site_id]
    site_lat, site_lon = site.iloc[0]["LAT"], site.iloc[0]["LON"]

    m = folium.Map(
        location=[site_lat, site_lon], zoom_start=12.3, tiles="CartoDB positron"
    )

    # Add iceberg shapefiles to the map
    site_path = os.path.join(
        SHAPEFILE_CATALOG_DIR, site_id, f"{early_date}-{later_date}"
    )
    if os.path.exists(site_path):
        shapefiles = [f for f in os.listdir(site_path) if f.endswith(".shp")]
        for iceberg in shapefiles:
            shp_path = os.path.join(site_path, iceberg)
            gdf = load_and_reproject_shapefile(shp_path)

            # Calculate width and height
            width, height = calculate_width_height(gdf)

            color = (
                "#7a1037"
                if early_date in iceberg
                else "#033b59"
                if later_date in iceberg
                else "gray"
            )
            popup_content = f"<strong>Iceberg ID:</strong> {iceberg}<br><strong>Width:</strong> {width} meters<br><strong>Height:</strong> {height} meters"

            # Add GeoJson to map with popups
            folium.GeoJson(
                gdf.__geo_interface__,
                name=iceberg,
                style_function=lambda x, color=color: {"color": color, "weight": 1},
                popup=folium.Popup(popup_content, max_width=300),
            ).add_to(m)

            # Zoom into iceberg centroid
            centroid = gdf.geometry.centroid.iloc[0]
            m.location = [centroid.y, centroid.x]
            m.zoom_start = 12

    return m

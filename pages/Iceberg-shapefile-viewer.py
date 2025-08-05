import streamlit as st
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.affinity import translate
import io

SHAPEFILE_CATALOG_DIR = "catalog-data/iceberg-shapefiles"

# Title of the page with description:
st.title("🔍👀 Iceberg Shapefile Viewer:")
st.markdown("❄️This page will allow you to explore iceberg varying iceberg shapes and sizes using shapefiles.")
st.markdown("The plots will automatically adjust the axis boundaries based on the largest iceberg, which ensures proper scaling for comparative analysis. The icebergs are color-coded by date, with orange representing the earlier date and green representing the later date.")
st.markdown("The shapefiles are then divided into four groups based on area, simplifying the identification of patterns in shape and size. Each group is displayed in its dedicated subplot, with overlapping shapes displayed in low opacity. This will hopefully expose the trends and variations across groups while preserving individual details.")

#The spreadsheet in the link below will display the available data:
st.info('Click here for the [Fjord Abbreviation List & Paired Dates](https://docs.google.com/spreadsheets/d/1kCcKqf717kK3_Xx-GDe0f61jhlUpZ5n6BN1qtiw7S4w/edit?gid=0#gid=0)')

# User interactions
with st.container():
    st.header("Filter")
    menu_col1, menu_col2, menu_col3 = st.columns(3)

#This will load the shapefiles, they will plot whether they exist within the folders or not.
if os.path.exists(SHAPEFILE_CATALOG_DIR):
    site_names = [
        name for name in sorted(os.listdir(SHAPEFILE_CATALOG_DIR) )
        if os.path.isdir(os.path.join(SHAPEFILE_CATALOG_DIR, name))
    ]

    # The default option the first found
    default_site_name = site_names[0]
    with menu_col1:
        site_name = st.selectbox(
            "Select Site Name",
            site_names,
            index=site_names.index(default_site_name) if default_site_name in site_names else 0,
            key="site_name_selectbox"
        )

    #This will get all of the available data for the date folders for the selected site, then it will sort the dates.
    if site_name:
        site_path = os.path.join(SHAPEFILE_CATALOG_DIR, site_name)
        date_folders = [folder for folder in os.listdir(site_path) if '-' in folder]
        date_folders.sort() 
        
        #This will Pre-load dates based on the available folders. The default date range is set here and it can be changed if you'd like.
        date_options = [
            (folder.split('-')[0], folder.split('-')[1])
            for folder in date_folders
        ]
        date_options = [
            (start_date, end_date) for start_date, end_date in date_options
        ]

        default_date_range = date_folders[0]
        default_dates = (default_date_range.split('-')[0], default_date_range.split('-')[1])

        with menu_col2:
           #Dropdown menu customization:
            selected_dates = st.selectbox(
                "Select Date Range",
                date_options,
                index=date_options.index(default_dates) if default_dates in date_options else 0,
                key="date_range_selectbox"
            )
        
        if selected_dates:
            early_date, late_date = selected_dates
            date_range_folder = f"{early_date}-{late_date}"
            target_folder = os.path.join(site_path, date_range_folder)

            if os.path.exists(target_folder):
                shapefiles = [
                    file for file
                    in os.listdir(target_folder) if file.endswith('.shp')
                ]

                if shapefiles:
                    st.subheader(f"Displaying {len(shapefiles)} Shapefiles")

                    max_width, max_height = 0, 0
                    shapefile_metadata = []
                    area_data = []

                    for filename in shapefiles:
                        shapefile_path = os.path.join(target_folder, filename)
                        gdf = gpd.read_file(shapefile_path)

                        if gdf.crs is None:
                            gdf = gdf.set_crs('EPSG:3413')
                        gdf = gdf.to_crs('EPSG:3413')

                        if not gdf.empty:
                            overall_bounds = gdf.total_bounds
                            width = overall_bounds[2] - overall_bounds[0]
                            height = overall_bounds[3] - overall_bounds[1]
                            max_width = max(max_width, width)
                            max_height = max(max_height, height)

                            area = gdf.area.sum() 
                            area_data.append(area)

                            shapefile_metadata.append((filename, gdf, width, height))

                    num_columns = 3
                    cols = st.columns(num_columns)

                    for i, (filename, gdf, width, height) in enumerate(shapefile_metadata):
                        col = cols[i % num_columns]
                        with col:
                            fig, ax = plt.subplots(figsize=(6, 6))
                            color = '#f5a442' if early_date in filename else '#8bc34a'

                            overall_bounds = gdf.total_bounds
                            gdf['geometry'] = gdf['geometry'].apply(lambda geom: translate(geom, -overall_bounds[0], -overall_bounds[1]))

                            gdf.plot(ax=ax, color=color, edgecolor='black', alpha=0.8, linewidth=2)

                            ax.set_xlim(0, max_width)
                            ax.set_ylim(0, max_height)
                            ax.set_xlabel("Width (m)")
                            ax.set_ylabel("Height (m)")
                            ax.set_title(filename, fontsize=10)
                            ax.axis("on")

                            st.pyplot(fig)

                    # This will display an iceberg area information table, necessary for quartile sorting:
                    area_df = pd.DataFrame({"Shapefile": shapefiles, "Area (m²)": area_data})
                    st.subheader("Iceberg Area Information:")
                    st.dataframe(area_df)

#This codeblock is helpful for debugging, locating missing files, and ensuring that the path to data is correct:
                else:
                    st.error(f"No shapefiles found in the folder: {target_folder}") 
            else:
                st.error(f"Target folder '{target_folder}' does not exist. Please check the dates and site name.")
        else:
            st.info("Please select a date range to proceed!")
else:
    st.error(f"Base path '{SHAPEFILE_CATALOG_DIR}' does not exist. Please check your folder structure.")

# This function will calculate the dominant angle of the iceberg shapes, so that they plot a little nicer and more uniform. It will use the average dominant angle.
def calculate_dominant_angle(gdf):
    """Calculate the dominant angle for the geometry in the shapefile."""
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

st.title("📊 Quartile-Based Iceberg Shape Comparison")
area_df["Quartile"] = pd.qcut(area_df["Area (m²)"], 4, labels=["Q1", "Q2", "Q3", "Q4"])

#Change the colors of the quartiles using the Hex Color picker:
quartile_colors = {"Q1": "#8bd67a", "Q2": "#e080d7", "Q3": "#f7bf07", "Q4": "#f78307"}
quartile_opacity = {"Q1": 0.4, "Q2": 0.4, "Q3": 0.4, "Q4": 0.4}

# This will help with consistent scaling:
max_width, max_height = 0, 0
for shapefile in area_df["Shapefile"]:
    shapefile_path = os.path.join(target_folder, shapefile)
    gdf = gpd.read_file(shapefile_path)
    
    if gdf.crs is None:
        gdf = gdf.set_crs('EPSG:3413')
    gdf = gdf.to_crs('EPSG:3413')
    
    if not gdf.empty:
        bounds = gdf.total_bounds
        max_width = max(max_width, bounds[2] - bounds[0])
        max_height = max(max_height, bounds[3] - bounds[1])

# Subplot customization:
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
            gdf = gdf.set_crs('EPSG:3413') #Proper projection for Greenland; this value will change depending on where your data is!
        gdf = gdf.to_crs('EPSG:3413')
        
        color = quartile_colors[quartile]
        opacity = quartile_opacity[quartile]

        overall_bounds = gdf.total_bounds
        gdf['geometry'] = gdf['geometry'].apply(lambda geom: translate(geom, -overall_bounds[0], -overall_bounds[1]))

        gdf.plot(ax=ax, color=color, edgecolor='black', alpha=opacity, linewidth=2)
    
    ax.set_xlim(0, max_width)
    ax.set_ylim(0, max_height)
    ax.set_xlabel("Width (m)")
    ax.set_ylabel("Height (m)")

#Plot the figure!
st.pyplot(fig)

# This will allow you to save the image as a .png file. 
image_stream = io.BytesIO()
fig.savefig(image_stream, format='png', bbox_inches="tight")
image_stream.seek(0)

st.download_button(
    label="💾 Save Image",
    data=image_stream,
    file_name="quartile_icebergs.png",
    mime="image/png"
)

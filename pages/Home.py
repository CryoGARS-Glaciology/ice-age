import streamlit as st

from modules.database import db_exists
from modules.plotting import last_viewed_site, map_overlay_css, overview_map
from modules.styling import metric_tile
from modules.ui_elements import GLACIER_ID_KEY, shapes_button, statistics_button

st.markdown(
    """
    <style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    </style>
    """,
    unsafe_allow_html=True,
)

st.html(
    """
    <h1 style="font-family: 'Poppins', sans-serif; font-weight: 700;
               font-size: 2.5rem; margin: 0 0 0.5rem 0; line-height: 1.2;">
        <span style="color: #0047AB;">ICE-AGE</span><span style="color: #0B2545;">:</span>
        <span style="color: #0E7C9E;">Iceberg Catalog for Analysis of Greenland Environments</span>
    </h1>
    """
)
st.markdown(
    "ICE-AGE is a research tool for exploring iceberg identification, "
    "metrics, and imagery across Greenland's coastal waters."
)

if db_exists():
    st.header("Study Sites in Greenland", divider=True)
    map_overlay_css()

    with st.container(key="glacier-map-container"):
        with st.container(key="glacier-map"):
            map_click = overview_map("ESRI")

        with st.container(key="glacier-options"):
            if map_click:
                site = last_viewed_site(map_click)
                if site:
                    st.markdown(f"__Name__: {site['Official_name']}")
                    if site.get("has_shapes", False):
                        shapes_button(site[GLACIER_ID_KEY])
                    if site.get("has_statistics", False):
                        statistics_button(site[GLACIER_ID_KEY])
                else:
                    st.markdown("""
                    Select a glacier site to see options.
                    
                    **Map Legend:**
                    """)
                    with st.container(key="legend"):
                        st.html(
                            '<i class="fa-solid fa-map-marker" style="color: #0047AB; margin-right: 8px;"></i>Data available<br>'
                            '<i class="fa-solid fa-map-marker" style="color: #808080; margin-right: 8px;"></i>No data available'
                        )
else:
    st.header("Setup Instructions", divider=True)
    st.text(
        "To use the ICE-AGE catalog, you will need to set up the database and import "
        "the underlying data from a published Zenodo data set. Please go to the "
        "Data Import page for instructions."
    )
    if st.button("Go to Data Import", type="primary"):
        st.switch_page("pages/Data-Import.py")

st.header("Available Iceberg Metrics", divider=True)
metric_cols = st.columns(3)
with metric_cols[0]:
    metric_tile("📍", "Location, repeat imagery metadata, and identification for iceberg studies.")
with metric_cols[1]:
    metric_tile("🧊", "Access code for shapefiles to connect to ICE-AGE metrics.")
with metric_cols[2]:
    metric_tile("📏", "Iceberg size, volume, draft, and submerged area data.")

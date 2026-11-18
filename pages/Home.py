import streamlit as st

from modules.database import db_exists
from modules.map_backgrounds import map_style_selector
from modules.plotting import last_viewed_site, overview_map
from modules.style_helper import load_css
from modules.ui_elements import GLACIER_ID_KEY, shapes_button, statistics_button

load_css("pages/home.css", "pages/maps.css")

st.html(
    """
    <h1 class="home-title">
        <span class="name">ICE-AGE</span><span class="colon">:</span>
        <span class="subtitle">Iceberg Catalog for Analysis of Greenland Environments</span>
    </h1>
    """
)

st.text(
    "The ICE-AGE catalog is a powerful tool for iceberg research, offering "
    "easy access to iceberg identification, metrics, and imagery."
)

if db_exists():
    st.header("Study Sites in Greenland", divider=True)
    map_style = map_style_selector()

    with st.container(key="glacier-map-container"):
        with st.container(key="glacier-map"):
            map_click = overview_map(map_style)

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
                            '<i class="fa-solid fa-map-marker legend-icon-available"></i>Data available<br>'
                            '<i class="fa-solid fa-map-marker legend-icon-missing"></i>No data available'
                        )
else:
    st.header("Setup instructions", divider=True)
    st.text(
        "To use the ICE-AGE catalog, you will need to set up the database and import "
        "the underlying data from a published Zenodo data set. Please go to the "
        "Data Import page for instructions."
    )
    if st.button("Go to Data Import", type="primary"):
        st.switch_page("pages/Data-Import.py")

st.header("Available Iceberg Metrics", divider=True)
METRICS = [
    ("📍", "Location, repeat imagery metadata, and identification for iceberg studies."),
    ("🧊", "Access code for shapefiles to connect to ICE-AGE metrics."),
    ("📏", "Iceberg size, volume, draft, and submerged area data."),
]
metric_cols = st.columns(3)
for col, (icon, label) in zip(metric_cols, METRICS):
    with col:
        st.html(
            f"""
            <div class="metric-tile">
                <span class="metric-tile-icon">{icon}</span>
                <span class="metric-tile-label">{label}</span>
            </div>
            """
        )

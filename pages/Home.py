import streamlit as st

from modules.database import db_exists
from modules.map_backgrounds import map_style_selector
from modules.plotting import last_viewed_site, overview_map

st.html(
    """
    <h1 style="
        font-family: 'Bungee Shade', 'Audiowide', sans-serif;
        font-size: 40px;
        text-align: center;
        background: linear-gradient(90deg, #9c27b0, #e91e63, #ff5722, #ffeb3b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;">
        ICE-AGE Innovation: Empowering Iceberg Analysis in Greenland Environments
    </h1>
    """,
)

st.text(
    "The ICE-AGE catalog is a powerful tool for iceberg research, offering "
    "easy access to iceberg identification, metrics, and imagery."
)

if db_exists():
    st.header("Study Sites in Greenland", divider=True)
    map_style = map_style_selector()
    map_click = overview_map(map_style)

    if map_click:
        site = last_viewed_site(map_click)
        if site:
            st.switch_page("pages/Iceberg-Viewer.py", query_params={"site_id": site})
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

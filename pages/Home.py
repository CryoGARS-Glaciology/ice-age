import streamlit as st

from modules.plotting import last_viewed_site, overview_map
from modules.ui_elements import map_style_selector

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

# Brief description of the app
st.text(
    "The ICE-AGE catalog is a powerful tool for iceberg research, offering "
    "easy access to iceberg identification, metrics, and imagery."
)

map_style = map_style_selector()
st.sidebar.info(
    "ICE-AGE will be under steady development and the data updated continuously! "
    "The Data will be archived at the Arctic Data Center and web app source code is "
    "available via GitHub. "
)


# Create the map with interactive controls in an expandable section
st.header("Study Sites in Greenland", divider=True)
map_click = overview_map(map_style)
st.markdown("Years represented in study: 2011 - 2023")

if map_click:
    site = last_viewed_site(map_click)
    if site:
        st.switch_page("pages/Iceberg-Viewer.py", query_params={"site_id": site})

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

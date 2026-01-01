import streamlit as st

from modules.plotting import overview_map

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

# You can alter the map properties here:
map_style = st.sidebar.selectbox(
    "Select Map Style",
    options=["CartoDB positron", "CartoDB dark_matter"],
    index=0,  # This line sets the default, change to 1 for dark_matter default.
)
st.sidebar.info(
    "ICE-AGE will be under steady development and the data updated continuously! "
    "The Data will be archived at the Arctic Data Center and web app source code is "
    "available via GitHub. "
)


# Create the map with interactive controls in an expandable section
st.header("Study Sites in Greenland", divider=True)
overview_map(map_style)
st.markdown("Years represented in study: 2011 - 2023")

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

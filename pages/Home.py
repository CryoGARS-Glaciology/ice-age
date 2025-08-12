import streamlit as st

from modules.plotting import distribution_plot, overview_map

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


# Create the map with interactive controls in an expandable section
with st.expander("🗺️ Map of Greenland with selected study sites", expanded=True):
    overview_map(map_style)

st.markdown("Years represented in study: 2011 - 2023")

with st.expander("How to access ICE-AGE:", expanded=True):
    st.text(
        "ICE-AGE data will be archived at the Arctic Data Center. "
        "Code is available via GitHub, and Zenodo for future growth "
        "and automated figure generation."
    )

st.title("Contents of ICE-AGE application:")

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

# Distribution plot
st.pyplot(distribution_plot())

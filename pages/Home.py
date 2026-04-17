import streamlit as st

from modules.database import db_exists
from modules.map_backgrounds import map_style_selector
from modules.plotting import last_viewed_site, map_overlay_css, overview_map

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
    map_overlay_css()
    map_style = map_style_selector()

    with st.container(key="glacier-map-container"):
        with st.container(key="glacier-map"):
            map_click = overview_map(map_style)

        with st.container(key="glacier-options"):
            if map_click:
                site = last_viewed_site(map_click)
                if site:
                    st.markdown(f"__Name__: {site['Official_name']}")

                    if site.get("has_shapes", False) or site.get(
                        "has_statistics", False
                    ):
                        if st.button(
                            "View Shapes", use_container_width=True, key="shapes-button"
                        ):
                            st.switch_page(
                                "pages/Iceberg-Viewer.py",
                                query_params={"site_id": site["Glacier_ID"]},
                            )
                        if st.button(
                            "Show Statistics",
                            use_container_width=True,
                            key="statistics-button",
                        ):
                            st.switch_page(
                                "pages/Statistics-dashboard.py",
                                query_params={"site_id": site["Glacier_ID"]},
                            )
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

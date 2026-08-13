import streamlit as st

from modules.database import db_exists
from modules.styling import inject_global_styles

# Application entry point
#
# # Site structure
#   * Home - Start page
#   * Iceberg Viewer - Interactive map to see spatial orientation of icebergs
#   * Statistics Dashboard - Loads and displays iceberg melt information and associated statistics.
#   * Melt Rates - Compares iceberg melt rates across all glacier systems.
#   * Research Methods - Displays the methods used for data generation and work flow
#   * Field Work Experiences - Fun pictures from the field!
#   * Acknowledgements - Displays authors and award numbers.

if db_exists():
    data_pages = [
        st.Page("pages/Iceberg-Viewer.py", title="Iceberg Viewer"),
        st.Page("pages/Statistics-dashboard.py", title="Statistics Dashboard"),
        st.Page("pages/Melt-Rates.py", title="Melt Rates"),
    ]
else:
    data_pages = []

data_pages += [
    st.Page("pages/Data-Import.py", title="Data Import"),
]

st.set_page_config(layout="wide", page_title="ICE-AGE")
inject_global_styles()
pg = st.navigation(
    {
        "": [
            st.Page("pages/Home.py", title="Home", default=True)
        ],
        "Data": data_pages,
        "About" : [
            st.Page("pages/Research-methods.py", title="Research Methods"),
            st.Page("pages/Field-Work-images.py", title="Field Work"),
            st.Page("pages/Image-Gallery.py", title="Image Gallery"),
            st.Page("pages/Acknowledgements.py", title="Acknowledgements"),
        ]
    }
)

pg.run()

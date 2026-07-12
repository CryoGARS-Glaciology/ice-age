import streamlit as st

from modules.database import db_exists

# Application entry point
#
# # Site structure
#   * Home - Start page
#   * Iceberg Viewer - Interactive map to see spatial orientation of icebergs
#   * Statistics Dashboard - Loads and displays iceberg melt information and associated statistics.
#   * Research Methods - Displays the methods used for data generation and work flow
#   * Field Work Experiences - Fun pictures from the field!
#   * Acknowledgements - Displays authors and award numbers.

if db_exists():
    data_pages = [
        st.Page("pages/Iceberg-Viewer.py"),
        st.Page("pages/Statistics-dashboard.py"),
    ]
else:
    data_pages = []

data_pages += [
    st.Page("pages/Data-Import.py"),
]

st.set_page_config(layout="wide")
pg = st.navigation(
    {
        "": [
            st.Page("pages/Home.py", default=True)
        ],
        "Data": data_pages,
        "About" : [
            st.Page("pages/Research-methods.py"),
            st.Page("pages/Field-Work-images.py"),
            st.Page("pages/Image-Gallery.py"),
            st.Page("pages/Acknowledgements.py"),
        ]
    }
)

# Clear data previous app runs
st.cache_data.clear()

pg.run()

import streamlit as st

# Application entry point
#
# # Site structure
#   * Home - Start page
#   * Iceberg Viewer - Interactive map to see spatial orientation of icebergs
#   * Statistics Dashboard - Loads and displays iceberg melt information and associated statistics.
#   * Research Methods - Displays the methods used for data generation and work flow
#   * Field Work Experiences - Fun pictures from the field!
#   * Acknowledgements - Displays authors and award numbers.

st.set_page_config(layout="wide")
pg = st.navigation(
    {
        "": [
            st.Page("pages/Home.py", default=True)
        ],
        "Data" : [
            st.Page("pages/Iceberg-Viewer.py"),
            st.Page("pages/Statistics-dashboard.py"),
            st.Page("pages/Data-Import.py")
        ],
        "About" : [
            st.Page("pages/Research-methods.py"),
            st.Page("pages/Field-Work-images.py"),
            st.Page("pages/Image-Gallery.py"),
            st.Page("pages/Acknowledgements.py"),
        ]
    }
)

pg.run()

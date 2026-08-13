import streamlit as st

from database.create_db import populate_db
from modules.database import clear_db_cache, db_exists, get_connection


def create_db():
    if db_exists():
        get_connection().disconnect()

    clear_db_cache()

    try:
        populate_db()
        st.toast("Database created.", icon="✅")
        st.rerun()
    except Exception as exc:
        st.error(f"Failed to populate database: {exc}")


st.title("Data Import")
st.header(
    "Instructions to create a local database for this application",
    divider=True,
)
st.markdown(
    "This page will guide you through the process on getting the downloaded Zenodo data "
    "into the local database to start exploring the data. The setup requires basic "
    "knowledge of the command line."
)
st.header("Steps", divider=True)
st.markdown(
    """
    ### 1. Download the data

    Download the catalog data archive:
    [ice-age_app_catalog-data.zip](https://drive.google.com/file/d/1d-Am__IgiIqlATwYyJXlJpQKYhfr2nFn/view)

    ### 2. Create a folder inside the application repository
    
    On your local machine, go to the root location where you copied the repository from GitHub. 
    ```
    cd /path/to/ice-age
    ```
    Create a new folder for the application data inside the repository. This will serve
    as the root folder for all the data files.
    ```
    mkdir catalog-data
    ```
    Note that the application expects the folder name needs to be __`catalog-data`__ for the 
    import process to work. 
    
    ### 3. Move the downloaded Zenodo data into the new folder
    
    Move the downloaded Zenodo data into the new location and unpack the archive. This
    process can use the native file explorer of your operating system.
    
    Once finished, your folder structure should look similar to this, with the file names
    matching the names of the Zenodo archive:
    ```
    catalog-data/
        meltrates-csv/
           APU_basic_iceberg_meltinfo.csv
           ...
        iceberg-shapefiles/
           APU_20210718-20210727_icebergs.shp
           ...
        images/
        Glacier-Locations.csv
    ```
    ### 4. Populate the database  
    
    Click the button below to populate the database with the data.
    """
)

if st.button("Populate DB", type="primary"):
    with st.spinner("Populating database..."):
        create_db()

if db_exists():
    st.markdown(
        """   
            ### 5. All done!
            
            You are now ready to explore the data. The side navigation bar now has additional
            entries under the __"Data"__ category. The homepage will now show the overview 
            map with all iceberg study sites in Greenland.
            """
    )
    if st.button("Home", type="primary"):
        st.switch_page("pages/Home.py")

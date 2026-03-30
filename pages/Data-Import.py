import streamlit as st

from database.create_db import populate_db
from modules.database import clear_db_cache, db_exists, get_connection


def create_db():
    if db_exists():
        get_connection().disconnect()

    clear_db_cache()

    try:
        populate_db()
    except Exception as exc:
        st.error(f"Failed to populate database: {exc}")
    else:
        st.toast("Database created.", icon="✅")
        get_connection()


st.title("Data Import")
st.header(
    "Instructions to create a local database for this application",
    divider=True,
)
st.markdown(
    "This page will guide you through the process on getting the downloaded data "
    "into the local database."
)
st.header("Steps", divider=True)
st.markdown(
    """
    ### Download the data from [Zenodo](https://zenodo.org/)
    
    All data for this app is publicly available on Zenodo.
    [LINK](https://)
    
    ### Create a folder inside the application repository
    
    On your local machine, go to the root of the cloned repository. 
    ```
    cd /path/to/ice-age
    ```
    Create a new folder for the data inside the repository.
    ```
    mkdir catalog-data
    ```
    Note that the folder name needs to be `catalog-data` for the import process to work. 
    
    ### Move the downloaded data into the new folder
    
    Once finished moving the data inside this folder, your folder structure should look like this:
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
    ### Populate the database  
    Click the button below to populate the database with the data.
    """
)

st.button(
    "Populate DB",
    on_click=create_db,
    type="primary",
)

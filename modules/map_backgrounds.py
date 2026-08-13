import streamlit as st

MAP_BACKGROUNDS = {
    "ESRI": {
        "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attribution": 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    },
    "Stadia": {
        "tiles": "https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.jpg",
        "attribution": '&copy; CNES, Distribution Airbus DS, © Airbus DS, © PlanetObserver (Contains Copernicus Data) | &copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    },
}


def map_style_selector() -> str:
    """
    Selector on the sidebar to change the map background.
    Calling this method will add the selector to the sidebar.

    :return:
        Currently selected map style as string
    """
    return st.sidebar.selectbox(
        "Select Map Style",
        options=list(MAP_BACKGROUNDS.keys()),
        index=0,
    )

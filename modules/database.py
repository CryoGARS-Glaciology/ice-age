import ibis
import streamlit as st


@st.cache_resource
def get_table(table):
    return CONNECTION.table(table)


@st.cache_resource
def get_connection():
    return ibis.duckdb.connect(DB_PATH, read_only=True, extensions=["spatial"])

DB_PATH = "catalog-data/ice_age.duckdb"
CONNECTION = get_connection()

LOCATIONS = get_table("locations")
MELT_RATES = get_table("meltrates")

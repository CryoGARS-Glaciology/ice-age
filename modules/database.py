import ibis
import streamlit as st

from database import DB_PATH


@st.cache_resource
def get_connection():
    return ibis.duckdb.connect(DB_PATH, read_only=True, extensions=["spatial"])


@st.cache_resource
def get_table(table):
    return get_connection().table(table)

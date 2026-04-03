from pathlib import Path

import ibis
import streamlit as st

from database import DB_PATH


@st.cache_resource
def db_exists():
    return Path(DB_PATH).exists()


@st.cache_resource
def get_connection():
    if db_exists():
        return ibis.duckdb.connect(DB_PATH, read_only=True, extensions=["spatial"])
    else:
        return None


@st.cache_resource
def db_table(table):
    if db_exists():
        return get_connection().table(table)
    else:
        return None


def clear_db_cache() -> None:
    """
    Clear all cached database connection info and tables.
    This is used when creating or reimporting the database.
    """
    db_exists.clear()
    db_table.clear()
    get_connection.clear()

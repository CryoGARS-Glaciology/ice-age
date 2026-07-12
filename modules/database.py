from pathlib import Path

import ibis
import streamlit as st

from database import DB_PATH


def db_exists():
    return Path(DB_PATH).exists()


@st.cache_resource
def connect_to_db():
    return ibis.duckdb.connect(DB_PATH, read_only=True, extensions=["spatial"])


def get_connection():
    """
    Wrapper to ensure only a successful connection is cached
    """
    if db_exists():
        return connect_to_db()
    else:
        return None


def db_table(table):
    if get_connection() is None:
        raise Exception("Database not connected")
    else:
        return get_connection().table(table)


def clear_db_cache() -> None:
    """
    Clear all cached database connection info and tables.
    This is used when creating or reimporting the database.
    """
    get_connection.clear()

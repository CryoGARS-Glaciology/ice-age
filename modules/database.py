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
    # Imported lazily to avoid a circular import (both modules import this one).
    from modules.melt_rates import melt_rate_observations, observation_month_range
    from modules.shape_viewer import map_data

    db_exists.clear()
    db_table.clear()
    get_connection.clear()
    map_data.clear()
    melt_rate_observations.clear()
    observation_month_range.clear()

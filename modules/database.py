import threading
from pathlib import Path

import ibis
import pandas as pd
import streamlit as st

from database import DB_PATH


def db_exists():
    return Path(DB_PATH).exists()


@st.cache_resource
def connect_to_db() -> tuple[ibis.duckdb, threading.Lock]:
    """
    Create a connection to the database and create a thread lock. The lock is needed
    to ensure thread safety when executing queries.

    :return:
        Tuple - DB connection, Thread lock
    """
    connection = ibis.duckdb.connect(DB_PATH, read_only=True, extensions=["spatial"])
    lock = threading.Lock()
    return connection, lock


def get_connection():
    """
    Wrapper to ensure only a successful connection is cached
    """
    if db_exists():
        return connect_to_db()
    else:
        return None


def db_table(table: str) -> ibis.Table:
    """
    Get an ibis table from the database connection

    :param:
        table: Table name

    :raises:
        Exception when database is not connected

    :return:
        Ibis table
    """
    if get_connection() is None:
        raise Exception("Database not connected")
    else:
        connection, _lock = get_connection()
        table = connection.table(table)

        return table


def execute_query(expression) -> pd.DataFrame:
    """
    Execute an ibis expression with a thread lock and return the result as a pandas DataFrame.

    :param:
        expression: Ibis expression to execute

    :return:
        Pandas DataFrame with the query result
    """
    _connection, lock = get_connection()
    with lock:
        return expression.execute()


def clear_db_cache() -> None:
    """
    Clear all cached database connection info and tables.
    This is used when creating or reimporting the database.
    """
    # Imported lazily to avoid a circular import (both modules import this one).
    from modules.melt_rates import melt_rate_observations, observation_month_range
    from modules.shape_viewer import map_data

    # The cache lives on connect_to_db; get_connection is a plain wrapper and
    # has no .clear().
    connect_to_db.clear()
    map_data.clear()
    melt_rate_observations.clear()
    observation_month_range.clear()

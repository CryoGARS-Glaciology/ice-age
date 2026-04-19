import geopandas as gpd
import ibis
import pandas as pd
import streamlit as st
from ibis import _
from ibis import selectors as s

from database import LOCATIONS_TABLE, MELT_RATES_TABLE, SHAPE_TABLE
from modules import DATE_FORMAT
from modules.database import db_table


def locations_with_shape() -> pd.DataFrame:
    """
    Return a Pandas DataFrame of all locations with a column to indicate if shapes
    are available for that location.

    :return:
        DataFrame with locations and shape availability
    """
    return (
        db_table(LOCATIONS_TABLE)
        .mutate(
            has_shapes=db_table(LOCATIONS_TABLE).Glacier_ID.isin(
                db_table(SHAPE_TABLE).SiteID
            ),
            has_statistics=db_table(LOCATIONS_TABLE).Glacier_ID.isin(
                db_table(MELT_RATES_TABLE).SiteID
            ),
        )
        .execute()
    )


def shape_dates_for_site(site_id: str) -> pd.DataFrame:
    """
    Load unique combinations of start and end dates with available shapes for a given site.

    :param site_id: Site ID to query

    :return:
        Dataframe with start and end dates
    """
    return (
        db_table(SHAPE_TABLE)
        .filter(db_table(SHAPE_TABLE).SiteID == site_id)
        .group_by(db_table(SHAPE_TABLE).IcebergID, db_table(SHAPE_TABLE).filename)
        .aggregate(
            start=db_table(SHAPE_TABLE).Date.min(),
            end=db_table(SHAPE_TABLE).Date.max(),
        )
        .select("start", "end")
        .mutate(
            start_date=_.start.strftime(DATE_FORMAT),
            end_date=_.end.strftime(DATE_FORMAT),
        )
        .order_by("start")
        .distinct()
    ).execute()


@st.cache_data
def map_data(site_select: dict, date_select: dict = None) -> gpd.GeoDataFrame:
    """
    Query the database and load all shapes for a given site and date range.
    If no date range is given then all shapes for that site are returned.

    :param site_select: Site ID to query
    :param date_select: Date range to filter to (Optional)

    :return:
        GeoDataFrame with all shapes for the given site and date range
    """
    user_selection = [db_table(SHAPE_TABLE).SiteID == site_select["Glacier_ID"]]
    if date_select:
        user_selection.append(
            db_table(SHAPE_TABLE).Date.isin([date_select["start"], date_select["end"]])
        )

    window = ibis.window(group_by=[_.IcebergID, _.filename], order_by=_.Date)
    shape_query = (
        db_table(SHAPE_TABLE)
        .filter(user_selection)
        .select(
            ~s.cols("Date", "filename"),
            date_rank=ibis.row_number().over(window),
            observed_date=db_table(SHAPE_TABLE).Date.strftime(DATE_FORMAT),
        )
    )

    return shape_query.to_pandas().set_crs("EPSG:3413")

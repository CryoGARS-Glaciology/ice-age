import geopandas as gpd
import pandas as pd
from ibis import _

from database import SHAPE_TABLE
from modules import DATE_FORMAT
from modules.database import get_table

SHAPES = get_table(SHAPE_TABLE)


def date_ranges_for_site(site_id: str) -> pd.DataFrame:
    """
    Query the database for unique combinations of start and end dates for a given site.

    :param site_id: Site ID to query

    :return:
        Dataframe with start and end dates
    """
    return (
        SHAPES.filter(SHAPES.SiteID == site_id)
        .group_by(SHAPES.IcebergID, SHAPES.filename)
        .aggregate(
            start=SHAPES.Date.min(),
            end=SHAPES.Date.max(),
        )
        .select("start", "end")
        .mutate(
            start_formatted=_.start.as_timestamp("%Y%m%d").date().strftime(DATE_FORMAT),
            end_formatted=_.end.as_timestamp("%Y%m%d").date().strftime(DATE_FORMAT),
        )
        .order_by("start")
        .distinct()
    ).execute()


def map_data(site_select: dict, date_select: dict = None) -> gpd.GeoDataFrame:
    """
    Query the database and load all shapes for a given site and date range.
    If no date range is given then all shapes for that site are returned.

    :param site_select: Site ID to query
    :param date_select: Date range to filter to (Optional)

    :return:
        GeoDataFrame with all shapes for the given site and date range
    """
    user_selection = [SHAPES.SiteID == site_select["Glacier_ID"]]
    if date_select:
        user_selection.append(
            SHAPES.Date.isin([date_select["start"], date_select["end"]])
        )
    return (
        SHAPES.filter(user_selection)
        .mutate(observed_date=SHAPES.Date.as_timestamp("%Y%m%d").strftime("%Y-%m-%d"))
        .to_pandas()
        .set_crs("EPSG:3413", inplace=True)
    )

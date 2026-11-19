import geopandas as gpd
import ibis
import pandas as pd
import streamlit as st
from ibis import _
from ibis import selectors as s
from shapely.geometry import LineString

from database import LOCATIONS_TABLE, MELT_RATES_TABLE, SHAPE_TABLE
from modules import DATE_FORMAT
from modules.database import db_table, execute_query


def locations_with_shape() -> pd.DataFrame:
    """
    Return a Pandas DataFrame of all locations with a column to indicate if shapes
    are available for that location.

    :return:
        DataFrame with locations and shape availability
    """
    expression = db_table(LOCATIONS_TABLE).mutate(
        has_shapes=_.Glacier_ID.isin(db_table(SHAPE_TABLE).SiteID),
        has_statistics=_.Glacier_ID.isin(db_table(MELT_RATES_TABLE).SiteID),
    )

    return execute_query(expression)


def shape_dates_for_site(site_id: str) -> pd.DataFrame:
    """
    Load unique combinations of start and end dates with available shapes for a given site.

    :param site_id: Site ID to query

    :return:
        Dataframe with start and end dates
    """
    expression = (
        db_table(SHAPE_TABLE)
        .filter(_.SiteID == site_id)
        .group_by(_.IcebergID, _.filename)
        .aggregate(start=_.Date.min(), end=_.Date.max())
        .select("start", "end")
        .mutate(
            start_date=_.start.strftime(DATE_FORMAT),
            end_date=_.end.strftime(DATE_FORMAT),
        )
        .order_by("start")
        .distinct()
    )

    return execute_query(expression)


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
    table = db_table(SHAPE_TABLE)
    observations = table.filter(table.SiteID == site_select["Glacier_ID"])

    if date_select:
        range_start, range_end = date_select["start"], date_select["end"]

        # Each iceberg's first and last date within its campaign file
        observations = observations.mutate(
            span_start=_.Date.min().over(group_by=[_.IcebergID, _.filename]),
            span_end=_.Date.max().over(group_by=[_.IcebergID, _.filename]),
        )

        # Keep campaigns where some iceberg spans exactly the selected range,
        # and only the observations inside that range
        observations = (
            observations.mutate(
                campaign_matches=(
                    (_.span_start == range_start) & (_.span_end == range_end)
                )
                .any()
                .over(group_by=_.filename)
            )
            .filter(_.campaign_matches & _.Date.between(range_start, range_end))
            .drop("span_start", "span_end", "campaign_matches")
        )

    # Find matching early and late observations
    window = ibis.window(group_by=[_.IcebergID, _.filename], order_by=_.Date)
    # For calculating distances
    early_centroid = _.geom.centroid()
    late_centroid = early_centroid.lead(1).over(window)
    late_date = _.Date.lead(1).over(window)
    days_elapsed = late_date.delta(_.Date, unit="days")
    distance_meters = early_centroid.distance(late_centroid).round(0)

    expression = observations.select(
        ~s.cols("Date", "filename"),
        date_rank=ibis.row_number().over(window),
        observed_date=_.Date.strftime(DATE_FORMAT),
        early_centroid_geom=early_centroid,
        late_centroid_geom=late_centroid,
        days_elapsed=days_elapsed,
        distance_meters=distance_meters,
    )
    return execute_query(expression).set_crs("EPSG:3413")


def shape_distances(data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calculate the distance between the early and late centroids for each shape.

    :param data: GeoDataFrame with shape data

    :return:
        GeoDataFrame with distance between early and late centroids
    """
    site_lines = data[
        (data["date_rank"] == 0) & data["late_centroid_geom"].notna()
    ]
    if site_lines.empty:
        return gpd.GeoDataFrame(
            {
                "IcebergID": [],
                "distance_meters": [],
                "days_elapsed": [],
                "velocity_m_per_day": [],
            },
            geometry=gpd.GeoSeries([], crs="EPSG:4326"),
        )
    line_geometries = [
        LineString([(early.x, early.y), (late.x, late.y)])
        for early, late in zip(
            site_lines["early_centroid_geom"], site_lines["late_centroid_geom"]
        )
    ]
    site_lines["velocity_m_per_day"] = (
        site_lines["distance_meters"] / site_lines["days_elapsed"]
    ).round(2)

    return gpd.GeoDataFrame(
        site_lines[
            ["IcebergID", "distance_meters", "days_elapsed", "velocity_m_per_day"]
        ],
        geometry=line_geometries,
        crs="EPSG:3413",
    ).to_crs(epsg=4326)

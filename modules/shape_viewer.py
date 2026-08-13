import math

import geopandas as gpd
import ibis
import pandas as pd
import streamlit as st
from ibis import _
from ibis import selectors as s
from shapely.geometry import LineString, Polygon

from database import LOCATIONS_TABLE, MELT_RATES_TABLE, SHAPE_TABLE
from modules import DATE_FORMAT, URL_DATE_FORMAT
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
            # Stable identifiers for URL round-tripping, independent of the
            # display format above.
            url_start=_.start.strftime(URL_DATE_FORMAT),
            url_end=_.end.strftime(URL_DATE_FORMAT),
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
    user_selection = table.SiteID == site_select["Glacier_ID"]
    if date_select:
        # Scope to the specific campaign file(s) whose (min, max) date matches
        # the selection, rather than matching Date by value site-wide: two
        # adjacent campaigns can share a boundary date (e.g. one ends and the
        # next begins on the same day), which would otherwise pull rows from
        # the wrong campaign into the same (IcebergID, filename) group below.
        campaign_dates = table.filter(user_selection).group_by(
            table.IcebergID, table.filename
        ).aggregate(start=table.Date.min(), end=table.Date.max())
        matching_files = (
            campaign_dates.filter(
                (campaign_dates.start == date_select["start"])
                & (campaign_dates.end == date_select["end"])
            )
            .select("filename")
            .distinct()
        )
        user_selection = user_selection & table.filename.isin(matching_files.filename)

    filtered = table.filter(user_selection)

    # De-duplicate to at most one row per (IcebergID, filename, Date): some
    # source shapefiles contain duplicate digitizations for the same
    # iceberg/date, which would otherwise make the early/late pairing below
    # (and the resulting distance) unreliable.
    dedup_window = ibis.window(group_by=[_.IcebergID, _.filename, _.Date])
    deduped = (
        filtered.mutate(_dup_rank=ibis.row_number().over(dedup_window))
        .filter(_._dup_rank == 0)
        .drop("_dup_rank")
    )

    # Find matching early and late observations
    window = ibis.window(group_by=[_.IcebergID, _.filename], order_by=_.Date)
    # For calculating distances
    early_centroid = _.geom.centroid()
    late_centroid = early_centroid.lead(1).over(window)
    late_date = deduped.Date.lead(1).over(window)
    days_elapsed = late_date.delta(deduped.Date, unit="days")
    distance_meters = early_centroid.distance(late_centroid).round(0)

    expression = deduped.select(
        # Keep filename (campaign): IcebergID is only a label local to one
        # campaign's shapefile and is reused across unrelated campaigns, so
        # (IcebergID, filename) together are needed downstream to tell two
        # actually-different icebergs apart (e.g. for map coloring).
        ~s.cols("Date"),
        date_rank=ibis.row_number().over(window),
        observed_date=deduped.Date.strftime(DATE_FORMAT),
        early_centroid_geom=early_centroid,
        late_centroid_geom=late_centroid,
        distance_meters=distance_meters,
        # Straight-line drift speed between this observation and the next
        # one for the same iceberg; null where there is no next observation
        # (the "late" row of a pair, or a singleton observation).
        velocity_m_per_day=(distance_meters / days_elapsed).round(1),
    )
    return execute_query(expression).set_crs("EPSG:3413")

def shape_distances(data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calculate the distance between the early and late centroids for each shape.

    :param data: GeoDataFrame with shape data

    :return:
        GeoDataFrame with distance between early and late centroids
    """
    site_lines = data[(data["date_rank"] == 0) & data["late_centroid_geom"].notna()]
    line_geometries = [
        LineString([(early.x, early.y), (late.x, late.y)])
        for early, late in zip(
            site_lines["early_centroid_geom"], site_lines["late_centroid_geom"]
        )
    ]
    return gpd.GeoDataFrame(
        site_lines[["IcebergID", "filename", "distance_meters", "velocity_m_per_day"]],
        geometry=line_geometries,
        crs="EPSG:3413",
    ).to_crs(epsg=4326)


def _arrowhead_polygon(start_x, start_y, end_x, end_y) -> Polygon:
    """
    Build a small triangle pointing from (start_x, start_y) toward
    (end_x, end_y), tip at the end point. Sized relative to the line's own
    length (capped) so it stays visible on both short and long displacements.

    :return:
        Triangle Polygon in the same (projected, meters) units as the input.
    """
    dx, dy = end_x - start_x, end_y - start_y
    length = math.hypot(dx, dy)
    if length == 0:
        length = 1.0
    ux, uy = dx / length, dy / length  # unit vector along the line
    px, py = -uy, ux  # unit vector perpendicular to the line

    arrow_len = min(max(length * 0.15, 35), 180)
    arrow_width = arrow_len * 0.55

    back_x, back_y = end_x - ux * arrow_len, end_y - uy * arrow_len
    left = (back_x + px * arrow_width / 2, back_y + py * arrow_width / 2)
    right = (back_x - px * arrow_width / 2, back_y - py * arrow_width / 2)
    return Polygon([(end_x, end_y), left, right])


def shape_arrowheads(data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Build a small directional arrowhead at the end (late observation) of
    each iceberg's displacement line, so its direction of travel is visible
    at a glance rather than only inferable from a plain line.

    :param data: GeoDataFrame with shape data (see :py:func:`map_data`)

    :return:
        GeoDataFrame of triangle Polygons, one per drawable displacement.
    """
    site_lines = data[(data["date_rank"] == 0) & data["late_centroid_geom"].notna()]
    arrow_geometries = [
        _arrowhead_polygon(early.x, early.y, late.x, late.y)
        for early, late in zip(
            site_lines["early_centroid_geom"], site_lines["late_centroid_geom"]
        )
    ]
    return gpd.GeoDataFrame(
        site_lines[["IcebergID", "filename"]],
        geometry=arrow_geometries,
        crs="EPSG:3413",
    ).to_crs(epsg=4326)
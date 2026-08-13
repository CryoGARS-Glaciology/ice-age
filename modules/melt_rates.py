import ibis
import pandas as pd
import streamlit as st
from ibis import _

from database import LOCATIONS_TABLE, MELT_RATES_TABLE
from modules.database import db_table

# Column labels shared by the charts, the raw-data table and the CSV export, so
# the units a reader sees on an axis are the same strings they get in the
# download.
MELT_RATE_LABEL = "Melt rate (m d⁻¹)"
DRAFT_LABEL = "Draft, mean (m)"
SURFACE_AREA_LABEL = "Surface area, mean (m²)"

# Numeric columns arrive from DuckDB as DECIMAL, which pandas surfaces as
# `object` dtype holding Decimal instances. Altair/Vega cannot encode those, so
# every measure is cast to float in the query rather than being patched up
# per-chart afterwards.
_MEASURES = {
    "melt_rate": "Melt_Rate",
    "melt_rate_uncertainty": "Melt_Rate_uncertainty",
    "draft": "Draft_mean",
    "surface_area": "Surface_Area_mean",
    "submerged_area": "Submerged_Area_mean",
    "volume_change": "dVdt_mean",
}

RAW_DATA_COLUMNS = {
    "site_id": "Site ID",
    "site": "Glacier System",
    "start": "Observation Start",
    "end": "Observation End",
    "melt_rate": MELT_RATE_LABEL,
    "melt_rate_uncertainty": "Melt rate uncertainty (m d⁻¹)",
    "draft": DRAFT_LABEL,
    "surface_area": SURFACE_AREA_LABEL,
    "submerged_area": "Submerged area, mean (m²)",
    "volume_change": "Volume change (m³ d⁻¹)",
}


@st.cache_data
def melt_rate_observations(site_ids: tuple[str, ...] | None = None) -> pd.DataFrame:
    """
    Load individual iceberg melt-rate observations across every glacier system.

    Unlike :py:func:`modules.statistics.load_statistics`, which serves the
    single-site dashboard, this returns one row per observed iceberg for *all*
    (or a chosen subset of) systems so they can be compared against each other
    on shared axes.

    :param site_ids: Optional tuple of Glacier IDs to restrict the result to.
                     A tuple (not a list) so the result stays cacheable.

    :return:
        DataFrame with one row per iceberg observation window, carrying both
        the Glacier ID and the official system name.
    """
    melt = db_table(MELT_RATES_TABLE)
    locations = db_table(LOCATIONS_TABLE)

    query = melt.join(locations, melt.SiteID == locations.Glacier_ID).select(
        site_id=melt.SiteID,
        site=locations.Official_name,
        start=melt.Date_start,
        end=melt.Date_end,
        **{
            alias: melt[column].cast("float")
            for alias, column in _MEASURES.items()
        },
    )

    if site_ids:
        query = query.filter(_.site_id.isin(list(site_ids)))

    observations = query.order_by([ibis.asc(_.site_id), ibis.asc(_.start)]).execute()
    # Month of the observation window's start, for seasonality encoding. Kept
    # out of the SQL projection because it is a display concern rather than a
    # stored measure, and it never reaches the CSV export (see raw_data_table).
    observations["month"] = observations["start"].dt.month
    return observations


@st.cache_data
def observation_month_range() -> tuple[int, int]:
    """
    Earliest and latest calendar month covered by the whole catalog.

    Deliberately computed across every site rather than from a filtered frame:
    it anchors the seasonal color scale, and a domain that moved with the site
    filter would repaint the surviving points on every selection change.

    :return:
        ``(first_month, last_month)`` as 1-12 integers.
    """
    months = (
        db_table(MELT_RATES_TABLE)
        .aggregate(
            first=_.Date_start.month().min(),
            last=_.Date_start.month().max(),
        )
        .execute()
    )
    return int(months["first"].iloc[0]), int(months["last"].iloc[0])


def site_summary(observations: pd.DataFrame) -> pd.DataFrame:
    """
    Rank glacier systems by their median melt rate.

    Aggregated in pandas rather than in a second database query: the caller
    already holds every observation it needs (the full catalog is on the order
    of a thousand rows), so re-querying would cost a round trip to compute
    something the in-memory frame already answers.

    The median — not the mean — sets the ranking because per-site sample sizes
    are small and uneven (single digits at some systems), where one unusually
    fast-melting iceberg would otherwise decide a system's position.

    :param observations: Frame from :py:func:`melt_rate_observations`.

    :return:
        One row per system with observation count, median and mean melt rate,
        and a ``label`` combining the Glacier ID with its sample size.
    """
    if observations.empty:
        return pd.DataFrame(
            columns=["site_id", "site", "observations", "median", "mean", "label"]
        )

    summary = (
        observations.groupby(["site_id", "site"], as_index=False)
        .agg(
            observations=("melt_rate", "size"),
            median=("melt_rate", "median"),
            mean=("melt_rate", "mean"),
        )
        .sort_values("median", ascending=False, ignore_index=True)
    )
    # The sample size rides along in the axis label so a reader can weigh a
    # system's spread against how many icebergs produced it, without needing a
    # second annotation layer on the chart.
    summary["label"] = summary["site_id"] + "  (n=" + summary["observations"].astype(str) + ")"
    return summary


def raw_data_table(observations: pd.DataFrame) -> pd.DataFrame:
    """
    Rename the query's internal column names to their labelled, unit-carrying
    equivalents for display and CSV export.

    :param observations: Frame from :py:func:`melt_rate_observations`.

    :return:
        DataFrame with human-readable column headers.
    """
    # Selecting the mapped columns explicitly keeps display-only fields (e.g.
    # the derived month) out of the table and the downloaded CSV.
    table = observations[list(RAW_DATA_COLUMNS)].copy()
    # Observation bounds are whole days: dropping the all-zero time component
    # keeps the table readable and the exported CSV free of "00:00:00" noise.
    for column in ("start", "end"):
        table[column] = table[column].dt.date
    return table.rename(columns=RAW_DATA_COLUMNS)

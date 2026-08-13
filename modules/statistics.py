import ibis
import pandas as pd
from ibis import _
from ibis.expr.types import Table

from database import MELT_RATES_TABLE
from modules import DATE_FORMAT, URL_DATE_FORMAT
from modules.database import db_table


def statistic_dates_for_site(site_name: str) -> pd.DataFrame:
    """
    Load available observation periods with statistics for a given site.

    :param site_name: Glacier ID from the dropdown

    :return:
        Dataframe with raw (for filtering) and formatted (for labels) dates
    """
    return (
        db_table(MELT_RATES_TABLE)
        .filter(_.SiteID == site_name)
        .select(
            start=_.Date_start,
            end=_.Date_end
        )
        .mutate(
            start_date=_.start.strftime(DATE_FORMAT),
            end_date=_.end.strftime(DATE_FORMAT),
            url_start=_.start.strftime(URL_DATE_FORMAT),
            url_end=_.end.strftime(URL_DATE_FORMAT),
        )
        .distinct()
        .order_by(ibis.asc(_.start))
    ).execute()


def filter_site(site_name: str, date: str = None) -> Table:
    """
    Shared helper method to filter results by site and optionally by start date.

    :param site_name: Site name to filter by
    :param date: Optionally further filter by date

    :return:
        Ibis table that can be fetched or further filtered
    """
    query = db_table(MELT_RATES_TABLE).filter(
        db_table(MELT_RATES_TABLE).SiteID == site_name
    )
    if date:
        query = query.filter(db_table(MELT_RATES_TABLE).Date_start == date)

    return query


def key_statistics(site_name: str, date: str = None) -> pd.DataFrame:
    """
    Get key statistics for a site name and optionally further filtered by date.

    The key statistics are the mean values by date range and contain the mean metrics for
        * Number of days in the date range
        * Mean Surface Area
        * Mean Draft
        * Mean change in volume (dVdt)
        * Melt Rate
        * Melt Rate Uncertainty
    and rounds them to two decimal places.

    :param site_name: Site name to filter by
    :param date: Optionally further filter by date

    :return:
        Dataframe with results.
    """
    table = filter_site(site_name, date).mutate(
        date_difference=db_table(MELT_RATES_TABLE).Date_end.delta(
            db_table(MELT_RATES_TABLE).Date_start, unit="days"
        )
    )

    return (
        table.group_by(db_table(MELT_RATES_TABLE).Date_start)
        .aggregate(
            [
                table.date_difference.mean().cast("int").name("Number of Days"),
                table.Surface_Area_mean.mean().round(2).name("Surface Area Mean (m²)"),
                table.Draft_mean.mean().round(2).name("Draft Mean (m)"),
                table.dVdt_mean.mean().round(2).name("Volume Change (m³ d⁻¹)"),
                table.Melt_Rate.mean().name("Melt Rate (m d⁻¹)"),
                table.Melt_Rate_uncertainty.mean().name("Melt Rate Uncertainty"),
            ]
        )
        .mutate(
            **{
                "Observation Start": db_table(MELT_RATES_TABLE).Date_start.strftime(
                    DATE_FORMAT
                ),
            }
        )
    ).execute()


def load_statistics(site_name: str, date: str = None) -> pd.DataFrame:
    """
    Load statistics for a site name and optionally filter by the observed
    time range.

    :param site_name: ID selected from the dropdown
    :param date:

    :return:
        DataFrame with raw csv data
    """
    return filter_site(site_name, date).execute()

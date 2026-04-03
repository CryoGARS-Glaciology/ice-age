import ibis
import pandas as pd
from ibis.expr.types import Table

from database import MELT_RATES_TABLE
from modules import DATE_FORMAT
from modules.database import db_table


def load_periods(site_name: str) -> pd.DataFrame:
    """
    Load available observation periods for a given site.

    :param site_name: Glacier ID from the dropdown

    :return:
        Dataframe with raw to start (for filtering) and formatted start and end date
        for dropdown label.
    """
    return (
        db_table(MELT_RATES_TABLE).filter(db_table(MELT_RATES_TABLE).SiteID == site_name)
        .mutate(
            start_date=db_table(MELT_RATES_TABLE).Date_start.strftime(DATE_FORMAT),
            end_date=db_table(MELT_RATES_TABLE).Date_end.strftime(DATE_FORMAT),
        )
        .select(db_table(MELT_RATES_TABLE).Date_start, "start_date", "end_date")
        .distinct()
        .order_by(ibis.asc(db_table(MELT_RATES_TABLE).Date_start))
        .execute()
    )


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
                table.Surface_Area_mean.mean().round(2).name("Surface Area Mean (m^2)"),
                table.Draft_mean.mean().round(2).name("Draft Mean (m)"),
                table.dVdt_mean.mean().round(2).name("Volume change (m^3/day)"),
                table.Melt_Rate.mean().name("Melt Rate (m/day)"),
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


def key_statistics_chart_data(site_name: str, date: str = None) -> pd.DataFrame:
    """
    Get key statistics data for the charts in the metrics display.
    See ::py:func:`key_statistics` for loaded columns.

    :param site_name: Site name to filter by
    :param date: Optionally further filter by date

    :return:
        Dataframe with results.
    """
    return (
        filter_site(site_name, date).select(
            [
                db_table(MELT_RATES_TABLE).Date_start.name("Observation Start"),
                db_table(MELT_RATES_TABLE).Surface_Area_mean.round(2).name(
                    "Surface Area Mean (m^2)"
                ),
                db_table(MELT_RATES_TABLE).Draft_mean.round(2).name("Draft Mean (m)"),
                db_table(MELT_RATES_TABLE).dVdt_mean.round(2).name(
                    "Volume change (m^3/day)"
                ),
                db_table(MELT_RATES_TABLE).Melt_Rate.name("Melt Rate (m/day)"),
                db_table(MELT_RATES_TABLE).Melt_Rate_uncertainty.name(
                    "Melt Rate Uncertainty"
                ),
            ]
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

import ibis
import pandas as pd
from ibis.expr.types import Table

from database import MELT_RATES_TABLE
from modules.database import get_table

DATE_FORMAT = "%Y-%m-%d"

def load_site_names() -> pd.DataFrame:
    """
    Load all available glacier site names.
    Used for user menus.

    :return:
        Dataframe with 'Glacier_ID' for filtering and a 'label' for dropdown label.
    """
    return (
        LOCATIONS.join(MELT_RATES, LOCATIONS.Glacier_ID == MELT_RATES.Site)
        .select(
            [
                LOCATIONS.Official_name.name("label"),
                LOCATIONS.Glacier_ID,
            ]
        )
        .distinct()
        .order_by(ibis.asc(LOCATIONS.Glacier_ID))
    ).execute()
MELT_RATES = get_table(MELT_RATES_TABLE)


def load_periods(site_name: str) -> pd.DataFrame:
    """
    Load available observation periods for a given site.

    :param site_name: Glacier ID from the dropdown

    :return:
        Dataframe with raw to start (for filtering) and formatted start and end date
        for dropdown label.
    """
    return (
        MELT_RATES.filter(MELT_RATES.Site == site_name)
        .mutate(
            start_date=MELT_RATES.Date_start.strftime(DATE_FORMAT),
            end_date=MELT_RATES.Date_end.strftime(DATE_FORMAT),
        )
        .select(MELT_RATES.Date_start, "start_date", "end_date")
        .distinct()
        .order_by(ibis.asc(MELT_RATES.Date_start))
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
    query = MELT_RATES.filter(MELT_RATES.Site == site_name)
    if date:
        query = query.filter(MELT_RATES.Date_start == date)

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
        date_difference=MELT_RATES.Date_end.delta(MELT_RATES.Date_start, unit="days")
    )

    return (
        table.group_by(MELT_RATES.Date_start)
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
        .mutate(**{"Observation Start": MELT_RATES.Date_start.strftime(DATE_FORMAT)})
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
                MELT_RATES.Date_start.name("Observation Start"),
                MELT_RATES.Surface_Area_mean.round(2).name("Surface Area Mean (m^2)"),
                MELT_RATES.Draft_mean.round(2).name("Draft Mean (m)"),
                MELT_RATES.dVdt_mean.round(2).name("Volume change (m^3/day)"),
                MELT_RATES.Melt_Rate.name("Melt Rate (m/day)"),
                MELT_RATES.Melt_Rate_uncertainty.name("Melt Rate Uncertainty"),
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

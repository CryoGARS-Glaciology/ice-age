import ibis
import pandas as pd

from modules.database import LOCATIONS, MELT_RATES


def load_site_names() -> pd.DataFrame:
    """
    Load all available glacier site names.

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
            start_date=MELT_RATES.Date_start.strftime("%Y-%m-%d"),
            end_date=MELT_RATES.Date_end.strftime("%Y-%m-%d"),
        )
        .select(MELT_RATES.Date_start, "start_date", "end_date")
        .distinct()
        .order_by(ibis.asc(MELT_RATES.Date_start))
        .execute()
    )


def load_statistics(site_name: str, date: str = None) -> pd.DataFrame:
    """
    Load statistics for a given location and optionally filter by the observed
    time range.

    :param site_name: ID selected from the dropdown
    :param date:

    :return:
        DataFrame with raw csv data
    """
    query = MELT_RATES.filter(MELT_RATES.Site == site_name)
    if date:
        query = query.filter(MELT_RATES.Date_start == date)

    return query.execute()

import ibis
import pandas as pd
import streamlit as st
from ibis import _
from ibis.expr.types import Table

from database import LOCATIONS_TABLE
from modules.database import db_table

GLACIER_ID_KEY = db_table(LOCATIONS_TABLE).Glacier_ID.get_name()

SITE_SELECTOR_KEY = "site_name_selector"
SITE_PARAM = "site_id"
DATE_RANGE_KEY = "date_range_selector"
DATE_PARAM = "date_range"


def site_and_date_query_params():
    query_params = st.query_params
    selected_site = query_params.get(SITE_PARAM, None)
    selected_dates = query_params.get(DATE_PARAM, None)
    return selected_site, selected_dates


def site_name_selector(join_table: Table, selected_site=None):
    """
    Create a dropdown menu with all available glacier site names.
    Optionally set the selected site for the dropdown.

    :param join_table: Table to join with locations.
    :param selected_site: Set index value of the dropdown to this site.

    :return:
        Streamlit selectbox object
    """
    options = load_site_names(join_table)

    if selected_site and (selected_site in options[GLACIER_ID_KEY].values):
        index = (options[GLACIER_ID_KEY] == selected_site).idxmax()
        index = int(index)  # Streamlit needs an int and not int64
    else:
        index = None

    return st.selectbox(
        "Site Name:",
        options.to_dict("records"),
        index=index,
        placeholder="Select a glacier site",
        format_func=lambda x: x["label"],
        key=SITE_SELECTOR_KEY,
        on_change=update_site_name_url_param,
    )


def update_site_name_url_param():
    """
    Site selector dropdown callback to update the browser URL and add the site ID
    query parameter.
    """
    st.query_params[SITE_PARAM] = st.session_state[SITE_SELECTOR_KEY][GLACIER_ID_KEY]
    # Clear the date range selection
    st.session_state[DATE_RANGE_KEY] = None
    update_date_range_url_param()


def date_range_selector(date_ranges: pd.DataFrame, selected_date_range=None):
    """
    Create a dropdown menu with all available observation date ranges for a site.
    Optionally set the selected date range for the dropdown.

    :param date_ranges: Pandas DataFrame with date ranges to show
    :param selected_date_range: Set index value of the dropdown to this date range.

    :return:
        Streamlit select UI object
    """
    if selected_date_range:
        start_date, _end_date = selected_date_range.split("_")
        index = date_ranges[date_ranges.start == start_date]["start"].idxmax()
        index = int(index)  # Streamlit needs an int and not int64
    else:
        index = None

    return st.selectbox(
        "Observation Periods (start - end):",
        date_ranges.to_dict("records"),
        index=index,
        placeholder="Filter to an observation period",
        format_func=lambda x: f"{x['start_date']} to {x['end_date']}",
        key=DATE_RANGE_KEY,
        on_change=update_date_range_url_param,
    )


def update_date_range_url_param():
    """
    Date range dropdown callback to update the browser URL and add the date
    range query parameter.
    """
    if st.session_state.get(DATE_RANGE_KEY, None) is not None:
        selection = st.session_state[DATE_RANGE_KEY]
        if selection:
            st.query_params[DATE_PARAM] = (
                f"{selection['start_date']}_{selection['end_date']}"
            )
    else:
        st.query_params.pop(DATE_PARAM, None)


def load_site_names(join_table) -> pd.DataFrame:
    """
    Load all available glacier site names.
    Used for user menus.

    :param join_table: Table to join with locations.
                       Requires a 'SiteID' column on that table.

    :return:
        Dataframe with 'Glacier_ID' for filtering and a 'label' for dropdown label.
    """
    return (
        db_table(LOCATIONS_TABLE)
        .join(join_table, db_table(LOCATIONS_TABLE).Glacier_ID == join_table.SiteID)
        .select(
            [
                db_table(LOCATIONS_TABLE).Official_name.name("label"),
                db_table(LOCATIONS_TABLE).Glacier_ID,
            ]
        )
        .distinct()
        .order_by(ibis.asc(db_table(LOCATIONS_TABLE).Glacier_ID))
    ).execute()

def _button_query_params(site: str, selected_date: str) -> dict:
    """
    Construct URL query parameters for switching pages via buttons.

    :param site: The glacier site ID.
    :param selected_date: The selected date range string.

    :return:
        Dictionary of query parameters.
    """
    query_param = {SITE_PARAM: site}

    if selected_date:
        query_param[DATE_PARAM] = selected_date

    return query_param


def shapes_button(site: str, selected_date: str, full_width=True, **kwargs):
    """
    Button to navigate to the Iceberg Viewer page.

    :param site: The glacier site ID.
    :param selected_date: The selected date range.
    :param full_width: Whether the button should use the full container width.
    :param kwargs: Additional arguments for the Streamlit button.
    """
    if st.button(
        "View Shapes", use_container_width=full_width, key="shapes-button", **kwargs
    ):
        st.switch_page(
            "pages/Iceberg-Viewer.py",
            query_params=_button_query_params(site, selected_date),
        )


def statistics_button(site: str, selected_date: str, full_width=True, **kwargs):
    """
    Button to navigate to the Statistics Dashboard page.

    :param site: The glacier site ID.
    :param selected_date: The selected date range.
    :param full_width: Whether the button should use the full container width.
    :param kwargs: Additional arguments for the Streamlit button.
    """
    if st.button(
        "Show Statistics",
        use_container_width=full_width,
        key="statistics-button",
        **kwargs,
    ):
        st.switch_page(
            "pages/Statistics-dashboard.py",
            query_params=_button_query_params(site, selected_date),
        )


def has_records(table: str, site_name: str) -> bool:
    """
    Check if a table has any records for a specific site ID.

    :param table: The name of the table to query.
    :param site_name: The site ID to filter by.

    :return:
        True if records exist, False otherwise.
    """
    return len(db_table(table).filter(_.SiteID == site_name).head(1).execute()) > 0

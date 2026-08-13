import ibis
import pandas as pd
import streamlit as st
from ibis import _
from ibis.expr.types import Table

from database import LOCATIONS_TABLE
from modules.database import db_table

GLACIER_ID_KEY = "Glacier_ID"

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
        # Default to the first available site so the page shows data
        # immediately instead of an empty "select a site" state.
        index = 0 if len(options) else None

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
        # Match against the stable url_start column (not the raw `start`
        # date, and not the display-formatted start_date, both of which are
        # sensitive to DATE_FORMAT/type coercion) so pre-selection from a
        # URL/deep-link is independent of the display date format.
        url_start, _url_end = selected_date_range.split("_")
        matches = date_ranges[date_ranges.url_start == url_start]
        index = int(matches["start"].idxmax()) if len(matches) else None
    else:
        index = None

    if index is None:
        # Default to the first available observation period so the page
        # shows data immediately instead of an empty "select a period" state.
        index = 0 if len(date_ranges) else None

    return st.selectbox(
        "Observation Periods (start – end):",
        date_ranges.to_dict("records"),
        index=index,
        placeholder="Filter to an observation period",
        format_func=lambda x: f"{x['start_date']} – {x['end_date']}",
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
                f"{selection['url_start']}_{selection['url_end']}"
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


def _button_query_params(site: str, selected_date: str | None) -> dict:
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


def shapes_button(site: str, selected_date: str = None, full_width=True, **kwargs):
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


def statistics_button(site: str, selected_date: str = None, full_width=True, **kwargs):
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

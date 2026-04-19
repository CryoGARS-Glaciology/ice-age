import streamlit as st

from database import MELT_RATES_TABLE, SHAPE_TABLE
from modules.database import db_table
from modules.statistics import (
    key_statistics,
    key_statistics_chart_data,
    load_statistics,
    statistic_dates_for_site,
)
from modules.ui_elements import (
    date_range_selector,
    has_records,
    shapes_button,
    site_and_date_query_params,
    site_name_selector,
)

selected_site, selected_dates = site_and_date_query_params()

with open("pages/statistics.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📊 Iceberg Statistics Dashboard")

with st.container():
    col1, col2 = st.columns(2, vertical_alignment="bottom")
    with col1:
        st.header("Filter")
    with col2:
        with st.container(horizontal_alignment="right"):
            if selected_site and has_records(SHAPE_TABLE, selected_site):
                shapes_button(
                    selected_site, selected_dates, full_width=False, type="primary"
                )
    menu_col1, menu_col2 = st.columns(2)

with menu_col1:
    site_name = site_name_selector(db_table(MELT_RATES_TABLE), selected_site)

date_range = None

if site_name:
    with menu_col2:
        available_dates = statistic_dates_for_site(site_name["Glacier_ID"])
        date_range = date_range_selector(available_dates, selected_dates)


def hide_button(site_name, date, metric_name):
    button_key = button_id(site_name, date, metric_name, True)
    st.session_state[button_key] = True


def button_id(site_name, date, metric_name, state=False):
    base_name = f"{site_name}_{date}_{metric_name}"
    if state:
        return base_name + "_visible"
    else:
        return base_name


@st.fragment
def load_chart(site_name, date, metric_name):
    button_key = button_id(site_name, date, metric_name, True)
    data_loaded = st.session_state.get(button_key, False)

    with st.expander("Chart"):
        if not data_loaded:
            if st.button(
                    "Load Data",
                    key=button_id(site_name, date, metric_name),
                    type="secondary",
                    on_click=hide_button,
                    args=(site_name, date, metric_name),
            ):
                st.session_state[button_key] = True
        else:
            with st.spinner("Loading chart"):
                chart_data = key_statistics_chart_data(site_name, date)
                st.line_chart(
                    data=chart_data[metric_name].astype("float"),
                    y_label=metric_name,
                    x_label="Observation #",
                )


def chart_container(column, site_name, row, metric_name):
    button_key = button_id(
        site_name["Glacier_ID"], row["Observation Start"], metric_name, True
    )
    st.session_state[button_key] = False

    with column.container():
        load_chart(
            site_name["Glacier_ID"], row["Observation Start"],
            metric_name
        )


if site_name:
    loader_args = dict(site_name=site_name["Glacier_ID"])
    if date_range:
        loader_args["date"] = date_range["start"]

    key_stats = key_statistics(**loader_args)
    data = load_statistics(**loader_args)

    st.header("Key Iceberg Statistics")
    for _, row in key_stats.iterrows():
        with st.container(width="stretch", border=True):
            with st.container(width="stretch"):
                columns = st.columns(4)

                for index, metric_name in enumerate(
                    [
                        "Observation Start",
                        "Draft Mean (m)",
                        "Melt Rate (m/day)",
                        "Melt Rate Uncertainty",
                    ]
                ):
                    if metric_name == "Observation Start":
                        label = f":material/date_range: {metric_name}"
                    else:
                        label = f"_{metric_name}_"

                    columns[index].metric(
                        label=label,
                        value=row[metric_name],
                    )
                    if metric_name != "Observation Start":
                        chart_container(columns[index], site_name, row, metric_name)

            with st.container(width="stretch"):
                columns = st.columns(4)

                for index, metric_name in enumerate(
                    [
                        "Number of Days",
                        "Surface Area Mean (m^2)",
                        "Volume change (m^3/day)",
                    ]
                ):
                    columns[index].metric(
                        label=f"_{metric_name}_", value=row[metric_name]
                    )
                    if metric_name != "Number of Days":
                        chart_container(columns[index], site_name, row, metric_name)

    st.write("## Raw data")
    st.dataframe(data)
    st.download_button(
        label="Download .csv file",
        help="Download the above shown data as a .csv file",
        data=data.to_csv(index=False),
        file_name="iceberg_melt_rates.csv",
        mime="text/csv",
    )

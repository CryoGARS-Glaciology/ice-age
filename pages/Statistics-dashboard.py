import streamlit as st

from modules.statistics import (
    load_site_names,
    load_statistics,
    load_periods,
    key_statistics,
)

st.title("📊 Iceberg Statistics Dashboard")

with st.container():
    st.header("Filter")
    menu_col1, menu_col2 = st.columns(2)

with menu_col1:
    site_name = st.selectbox(
        "Site Name:",
        load_site_names().to_dict("records"),
        index=None,
        placeholder="Select a glacier site",
        format_func=lambda x: x["label"],
    )

date_range = None

if site_name:
    with menu_col2:
        date_range = st.selectbox(
            "Observation Periods:",
            load_periods(site_name["Glacier_ID"]).to_dict("records"),
            index=None,
            placeholder="Filter to an observation period",
            format_func=lambda x: f"{x['start_date']} to {x['end_date']}",
        )

if site_name:
    loader_args = dict(site_name=site_name["Glacier_ID"])
    if date_range:
        loader_args["date"] = date_range["Date_start"]

    st.header("Key Statistics")
    key_stats = key_statistics(**loader_args)

    for _, row in key_stats.iterrows():
        with st.container(width="stretch", border=True):
            columns = st.columns(7)

            for index, metric_name in enumerate(
                [
                    "Observation Start",
                    "Number of Days",
                    "Draft Mean",
                    "Melt Rate",
                    "Melt Rate Uncertainty",
                    "Surface Area Mean",
                    "Volume change over time",
                ]
            ):
                columns[index].metric(label=metric_name, value=row[metric_name])

    st.write("### Raw data:")
    data = load_statistics(**loader_args)

    st.dataframe(data)
    st.download_button(
        label="Download .csv file",
        help="Download the above shown data as a .csv file",
        data=data.to_csv(index=False),
        file_name="iceberg_melt_rates.csv",
        mime="text/csv",
    )

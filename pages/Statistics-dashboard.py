import streamlit as st

from modules.statistics import (
    load_site_names,
    load_statistics,
    load_periods,
    key_statistics,
    key_statistics_chart_data,
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

    key_stats = key_statistics(**loader_args)
    chart_data = key_statistics_chart_data(**loader_args)
    data = load_statistics(**loader_args)

    st.header("Key Statistics")
    for _, row in key_stats.iterrows():
        row_chart_data = chart_data[
            chart_data["Observation Start"] == row["Observation Start"]
        ].reset_index()
        with st.container(width="stretch", border=True):
            with st.container(width="stretch"):
                columns = st.columns(4)

                for index, metric_name in enumerate(
                    [
                        "Observation Start",
                        "Draft Mean",
                        "Melt Rate",
                        "Melt Rate Uncertainty",
                    ]
                ):
                    columns[index].metric(
                        label=metric_name,
                        value=row[metric_name],
                    )
                    if metric_name != "Observation Start":
                        with columns[index].expander("Chart"):
                            st.line_chart(
                                data=row_chart_data[metric_name].astype("float"),
                                y_label=metric_name,
                                x_label="Observation #",
                            )

            with st.container(width="stretch"):
                columns = st.columns(4)

                for index, metric_name in enumerate(
                    [
                        "Number of Days",
                        "Surface Area Mean",
                        "Volume change over time",
                    ]
                ):
                    columns[index].metric(label=metric_name, value=row[metric_name])
                    if metric_name != "Number of Days":
                        with columns[index].expander("Chart"):
                            st.line_chart(
                                data=row_chart_data[metric_name].astype("float"),
                                y_label=metric_name,
                                x_label="Observation #",
                            )

    st.write("## Raw data")
    st.dataframe(data)
    st.download_button(
        label="Download .csv file",
        help="Download the above shown data as a .csv file",
        data=data.to_csv(index=False),
        file_name="iceberg_melt_rates.csv",
        mime="text/csv",
    )

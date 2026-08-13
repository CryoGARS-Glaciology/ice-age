import altair as alt
import streamlit as st

from database import MELT_RATES_TABLE, SHAPE_TABLE
from modules.statistics import key_statistics, load_statistics, statistic_dates_for_site
from modules.ui_elements import (
    date_range_selector,
    has_records,
    shapes_button,
    site_and_date_query_params,
    site_name_selector,
)

selected_site, selected_dates = site_and_date_query_params()

with open("pages/statistics.css", "r") as f:
    st.html(f"<style>{f.read()}</style>")

st.title("Iceberg Statistics Dashboard")

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
    site_name = site_name_selector(MELT_RATES_TABLE, selected_site)

date_range = None

if site_name:
    with menu_col2:
        available_dates = statistic_dates_for_site(site_name["Glacier_ID"])
        date_range = date_range_selector(available_dates, selected_dates)

CHART_METRICS = [
    "Melt Rate (m d⁻¹)",
    "Draft Mean (m)",
    "Surface Area Mean (m²)",
    "Volume Change (m³ d⁻¹)",
    "Melt Rate Uncertainty",
    "Number of Days",
]

if site_name:
    stats = key_statistics(site_name=site_name["Glacier_ID"])

    st.header("Key Iceberg Statistics", divider=True)
    st.caption(f"{len(stats)} observation window(s) at {site_name['label']}")

    chart_data = stats[["Observation Start"]].copy()
    for metric_name in CHART_METRICS:
        chart_data[metric_name] = stats[metric_name].astype("float")

    columns = st.columns(3)
    for index, metric_name in enumerate(CHART_METRICS):
        with columns[index % 3]:
            st.markdown(f"**{metric_name}**")
            # mark_line(point=...) always draws a visible marker per
            # observation, so single-observation-window sites (e.g. many
            # sites only have 1 window) still show something instead of an
            # empty-looking chart with no line to draw. The point is styled
            # distinctly from the line (larger, contrasting color, white
            # ring) so individual observations stand out clearly.
            chart = (
                alt.Chart(chart_data)
                .mark_line(
                    color="#2a78d6",
                    point=alt.OverlayMarkDef(
                        color="#eb6834", size=90, filled=True,
                        stroke="white", strokeWidth=1.5,
                    ),
                )
                .encode(
                    x=alt.X("Observation Start", axis=alt.Axis(labelAngle=-45)),
                    # zero=False: auto-scale to the data's own range so
                    # real variability is visible instead of being
                    # compressed against a y-axis anchored at 0.
                    y=alt.Y(metric_name, scale=alt.Scale(zero=False)),
                )
                .properties(height=220, padding={"left": 5, "right": 5, "top": 5, "bottom": 5})
                .configure_axis(labelFontSize=10, titleFontSize=11)
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(chart, use_container_width=True)

    loader_args = dict(site_name=site_name["Glacier_ID"])
    if date_range:
        loader_args["date"] = date_range["start"]
    data = load_statistics(**loader_args)

    st.header("Raw Data", divider=True)
    st.dataframe(data, height=250)
    st.download_button(
        label="Download .csv file",
        help="Download the above shown data as a .csv file",
        data=data.to_csv(index=False),
        file_name="iceberg_melt_rates.csv",
        mime="text/csv",
    )

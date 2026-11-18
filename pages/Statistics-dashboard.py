import altair as alt
import streamlit as st

from database import MELT_RATES_TABLE, SHAPE_TABLE
from modules.statistics import (
    key_statistics,
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
HEIGHT = 220


if site_name:
    loader_args = dict(site_name=site_name["Glacier_ID"])
    if date_range:
        loader_args["date"] = date_range["start"]

    stats = key_statistics(site_name=site_name["Glacier_ID"])

    st.header("Key Iceberg Statistics")
    st.markdown(
        '<div class="stats-note">'
        f"{len(stats)} observation window(s) for {site_name['label']}. "
        "Each chart shows every window."
        "</div>",
        unsafe_allow_html=True,
    )

    stats = stats.sort_values("Observation Start")

    chart_data = stats[["Observation Start"]].copy()
    for metric_name in CHART_METRICS:
        chart_data[metric_name] = stats[metric_name].astype("float")

    selected_start = date_range["start_date"] if date_range else None
    selected_rows = chart_data[chart_data["Observation Start"] == selected_start]

    columns = st.columns(3)
    for index, metric_name in enumerate(CHART_METRICS):
        with columns[index % 3]:
            st.markdown(f"**{metric_name}**")
            x_axis = alt.X("Observation Start", axis=alt.Axis(labelAngle=-45))
            y_axis = alt.Y(metric_name, scale=alt.Scale(zero=False))

            # A line needs two points to show anything, so markers keep
            # sites with a single observation window visible. Points are
            # styled distinctly from the line.
            line = (
                alt.Chart(chart_data)
                .mark_line(
                    color="#2a78d6",
                    point=alt.OverlayMarkDef(
                        color="#eb6834", size=90, filled=True,
                        stroke="white", strokeWidth=1.5,
                    ),
                )
                .encode(x=x_axis, y=y_axis)
            )

            # Grey band behind the selected window. Bar width follows the
            # category spacing, so it adjusts to the number of observations.
            # y/y2 fix the bar to the full plot height (HEIGHT).
            band = (
                alt.Chart(selected_rows)
                .mark_bar(color="#eef1f5", opacity=0.7, clip=True)
                .encode(
                    x=x_axis,
                    y=alt.value(0),
                    y2=alt.value(HEIGHT),
                )
            )

            # Navy dot on the selected window's point.
            selected_dot = (
                alt.Chart(selected_rows)
                .mark_point(color="#0B2545", size=140, filled=True)
                .encode(x=x_axis, y=y_axis)
            )

            chart = (
                alt.layer(band, line, selected_dot)
                .properties(height=HEIGHT, padding={"left": 5, "right": 5, "top": 5, "bottom": 5})
                .configure_axis(labelFontSize=10, titleFontSize=11)
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(chart, use_container_width=True)

    data = load_statistics(**loader_args)

    st.header("Raw Data", divider=True)
    if date_range:
        st.markdown(
            '<div class="stats-note">'
            f"You're viewing {date_range['start_date']} to {date_range['end_date']}. "
            "The table and CSV download use this period. "
            "The charts above always show every period."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="stats-note">'
            "You're seeing all observation periods. Pick a period above to filter "
            "this table and the CSV download. "
            "The charts above always show every period."
            "</div>",
            unsafe_allow_html=True,
        )
    st.dataframe(data, height=250)
    st.download_button(
        label="Download .csv file",
        help="Download the above shown data as a .csv file",
        data=data.to_csv(index=False),
        file_name="iceberg_melt_rates.csv",
        mime="text/csv",
    )

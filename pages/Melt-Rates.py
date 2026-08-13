import altair as alt
import streamlit as st

from database import MELT_RATES_TABLE
from modules.database import db_table
from modules.melt_rates import (
    DRAFT_LABEL,
    MELT_RATE_LABEL,
    SURFACE_AREA_LABEL,
    melt_rate_observations,
    observation_month_range,
    raw_data_table,
    site_summary,
)
from modules.styling import resample_colors
from modules.ui_elements import GLACIER_ID_KEY, load_site_names

# Cross-system melt rate comparison.
#
# The Statistics Dashboard answers "what happened at this one glacier?". This
# page answers the complementary question — "how do the systems compare to each
# other?" — so every chart here puts all selected systems on shared axes.

# Single hue throughout: color on this page never encodes identity (the system
# is already on an axis or a facet header), only magnitude. Slot-1 blue matches
# the Statistics Dashboard so the two pages read as one product.
BLUE = "#2a78d6"
GRIDLINE = "#e6e8eb"
INK_MUTED = "#5c6570"

# Melt rates span roughly three orders of magnitude (0.001–3.8 m d⁻¹), and a
# handful of fast-melting icebergs at one system set the top of that range. On a
# linear axis those few points push every other system into a sliver against
# zero, so the comparison charts use a log scale. Safe here because the catalog
# holds no zero or negative melt rates. Ticks are pinned to decades so the axis
# stays readable instead of showing Vega's default log labels.
LOG_TICKS = [0.001, 0.01, 0.1, 1]

# Month of observation gets jet, sampled into one discrete step per month.
# Chosen for maximum hue separation between neighbouring months: single-hue and
# perceptually-uniform ramps (viridis, plasma) both left adjacent months looking
# alike in a scatter this dense.
#
# Jet's known trade-offs are live here and are why the chart does not lean on
# color alone: it is not perceptually uniform (its cyan and yellow bands read as
# brighter than the ordering implies, so "later in the year" is harder to judge
# from a single dot), and it is not colorblind-safe. The click-to-isolate legend
# below is the fallback for both.
#
# Stops are literal because matplotlib is not a runtime dependency of the app;
# resample_colors interpolates them to however many months the catalog covers.
JET_STOPS = [
    "#000080", "#0000df", "#0028ff", "#0080ff", "#00d4ff", "#36ffc1", "#7dff7a",
    "#c1ff36", "#ffe600", "#ff9400", "#ff4700", "#df0000", "#800000",
]
# Color for points filtered out by the legend selection: a light neutral that
# stays visible as context without competing with the isolated month.
MUTED_POINT = "#d3d7dd"
MONTH_LABEL_EXPR = (
    "['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']"
    "[datum.value]"
)

st.title("Iceberg Melt Rates by System")
st.markdown(
    "Compare submarine melt rates across Greenland's glacier systems. Every "
    "chart below shows the selected systems on shared axes, so differences "
    "between them are read directly rather than by flipping between sites."
)

st.header("Filter", divider=True)

site_options = load_site_names(db_table(MELT_RATES_TABLE))

selected = st.multiselect(
    "Glacier systems:",
    options=site_options.to_dict("records"),
    # Every system is selected by default: the page's purpose is the
    # all-systems comparison, so it opens on that rather than on an empty
    # state the reader has to assemble first.
    default=site_options.to_dict("records"),
    format_func=lambda option: f"{option[GLACIER_ID_KEY]} — {option['label']}",
    placeholder="Select one or more glacier systems",
)

if not selected:
    st.info("Select at least one glacier system to see melt rate comparisons.")
    st.stop()

site_ids = tuple(option[GLACIER_ID_KEY] for option in selected)
observations = melt_rate_observations(site_ids)

if observations.empty:
    st.warning("No melt rate records found for the selected systems.")
    st.stop()

summary = site_summary(observations)
# Rank order is computed once and reused as the explicit sort for the
# distribution chart, so the axis order always matches the ranking in the
# summary table.
rank_order = summary["label"].tolist()
ranked_observations = observations.merge(summary[["site_id", "label"]], on="site_id")

st.header("Overview", divider=True)
overview = st.columns(4)
overview[0].metric("Systems", f"{len(summary)}")
overview[1].metric("Iceberg observations", f"{len(observations):,}")
overview[2].metric(
    "Median melt rate", f"{observations['melt_rate'].median():.2f} m d⁻¹"
)
overview[3].metric(
    "Observation span",
    f"{observations['start'].min():%Y}–{observations['end'].max():%Y}",
)

st.header("Melt Rate Distribution by System", divider=True)
st.caption(
    "Systems are ranked by median melt rate. The box spans the interquartile "
    "range, the whiskers reach 1.5× that range, and points beyond them are "
    "individual icebergs. Sample sizes vary widely between systems, so each "
    "label carries its observation count."
)

distribution = (
    alt.Chart(ranked_observations)
    .mark_boxplot(
        size=11,
        median=alt.MarkConfig(color="white", strokeWidth=1.5),
        outliers=alt.MarkConfig(color=BLUE, filled=True, opacity=0.45, size=18),
        rule=alt.MarkConfig(color=INK_MUTED, size=1),
    )
    .encode(
        y=alt.Y("label:N", sort=rank_order, title=None),
        x=alt.X(
            "melt_rate:Q",
            title=f"{MELT_RATE_LABEL}, log scale",
            scale=alt.Scale(type="log"),
            axis=alt.Axis(gridColor=GRIDLINE, values=LOG_TICKS, format=".3~f"),
        ),
        color=alt.value(BLUE),
    )
    # ~24px per system keeps the boxes from collapsing into each other when
    # all systems are selected, and keeps the chart compact when only a few are.
    .properties(height=max(180, 24 * len(summary)))
    .configure_axis(labelFontSize=11, titleFontSize=12, domainColor=GRIDLINE, tickColor=GRIDLINE)
    .configure_view(strokeWidth=0)
)
st.altair_chart(distribution, use_container_width=True)

with st.expander("Ranked summary table"):
    st.dataframe(
        summary[["site_id", "site", "observations", "median", "mean"]].rename(
            columns={
                "site_id": "Site ID",
                "site": "Glacier System",
                "observations": "Observations",
                "median": f"Median {MELT_RATE_LABEL.lower()}",
                "mean": f"Mean {MELT_RATE_LABEL.lower()}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

st.header("Melt Rate vs. Draft", divider=True)
st.caption(
    "Each point is one iceberg observation window, colored by the month the "
    "window opened. **Click a month in the legend to isolate it** — shift-click "
    "to compare several, click empty space to reset."
)

first_month, last_month = observation_month_range()
observed_months = list(range(first_month, last_month + 1))
month_colors = resample_colors(JET_STOPS, len(observed_months))

# Clicking a month in the legend isolates it; shift-click builds up a set, and
# clicking empty space clears back to all months. Nine ordered colors can only
# be told apart so far in a scatter this dense, so this carries the part of the
# job the ramp cannot.
month_selection = alt.selection_point(fields=["month"], bind="legend")

scatter = (
    alt.Chart(observations)
    .mark_circle(size=45, stroke="white", strokeWidth=0.4)
    .encode(
        x=alt.X(
            "draft:Q",
            title=DRAFT_LABEL,
            axis=alt.Axis(gridColor=GRIDLINE, tickCount=10),
        ),
        y=alt.Y(
            "melt_rate:Q",
            title=f"{MELT_RATE_LABEL}, log scale",
            scale=alt.Scale(type="log"),
            axis=alt.Axis(gridColor=GRIDLINE, values=LOG_TICKS, format=".3~f"),
        ),
        color=alt.condition(
            month_selection,
            alt.Color(
                # Ordinal, not quantitative: a discrete swatch per month is far
                # easier to match back to a dot than a continuous gradient bar.
                "month:O",
                # The domain spans the whole catalog's months (see
                # observation_month_range) rather than the current selection, so
                # a given month keeps its color no matter which systems are
                # filtered in — and the scheme is resampled to that span.
                scale=alt.Scale(domain=observed_months, range=month_colors),
                legend=alt.Legend(
                    # Short title: the full "Month of observation" clips against
                    # the chart container's right edge, and the caption above
                    # already says what the color means.
                    title="Month",
                    labelExpr=MONTH_LABEL_EXPR,
                    symbolType="circle",
                    symbolSize=110,
                ),
            ),
            alt.value(MUTED_POINT),
        ),
        opacity=alt.condition(month_selection, alt.value(0.8), alt.value(0.3)),
        tooltip=[
            alt.Tooltip("site_id:N", title="Site"),
            alt.Tooltip("site:N", title="System"),
            alt.Tooltip("start:T", title="Observation start", format="%m/%d/%Y"),
            alt.Tooltip("start:T", title="Month", format="%B"),
            alt.Tooltip("melt_rate:Q", title=MELT_RATE_LABEL, format=".2f"),
            alt.Tooltip("draft:Q", title=DRAFT_LABEL, format=".1f"),
            alt.Tooltip("surface_area:Q", title=SURFACE_AREA_LABEL, format=",.0f"),
        ],
    )
    .add_params(month_selection)
    .properties(height=380)
    .configure_axis(labelFontSize=11, titleFontSize=12, domainColor=GRIDLINE, tickColor=GRIDLINE)
    .configure_view(strokeWidth=0)
)
st.altair_chart(scatter, use_container_width=True)

st.header("Melt Rate Through Time", divider=True)
st.caption(
    "One panel per system, sharing a log melt-rate axis (m d⁻¹) so panels are "
    "comparable at a glance. Each point is an observation window; a sparse "
    "panel means limited imagery coverage at that system, not slow melt."
)

timeline = (
    alt.Chart(ranked_observations)
    .mark_circle(size=28, opacity=0.6, color=BLUE)
    .encode(
        x=alt.X(
            "start:T",
            title=None,
            axis=alt.Axis(format="%Y", labelAngle=-45, gridColor=GRIDLINE, tickCount=3),
        ),
        y=alt.Y(
            "melt_rate:Q",
            # Titled in the caption instead of on the axis: Vega repeats an
            # axis title once per facet row, where it crowds and clips against
            # the panel to its left.
            title=None,
            scale=alt.Scale(type="log"),
            axis=alt.Axis(gridColor=GRIDLINE, values=LOG_TICKS, format=".3~f"),
        ),
        tooltip=[
            alt.Tooltip("site_id:N", title="Site"),
            alt.Tooltip("start:T", title="Observation start", format="%m/%d/%Y"),
            alt.Tooltip("end:T", title="Observation end", format="%m/%d/%Y"),
            alt.Tooltip("melt_rate:Q", title=MELT_RATE_LABEL, format=".2f"),
        ],
    )
    .properties(width=200, height=110)
    .facet(
        # Faceted rather than 29 colored lines on one axis: past a handful of
        # series no categorical palette stays distinguishable, and the panels
        # also make each system's temporal coverage visible.
        facet=alt.Facet("site_id:N", title=None, sort=summary["site_id"].tolist()),
        columns=6,
    )
    # An axis per panel, not one per column. The site count rarely fills the
    # grid exactly (29 systems across 6 columns leaves the last row short), and
    # with column-level axes the short columns draw their axis down at the
    # grid's baseline — which reads as a phantom, dataless panel sitting in the
    # gap. The scale stays shared, so panels remain comparable.
    .resolve_axis(x="independent")
    .configure_axis(labelFontSize=10, titleFontSize=11, domainColor=GRIDLINE, tickColor=GRIDLINE)
    .configure_view(strokeWidth=0)
    .configure_header(labelFontSize=11, labelFontWeight="bold")
)
st.altair_chart(timeline, use_container_width=True)

st.header("Raw Data", divider=True)
data = raw_data_table(observations)
st.dataframe(data, height=250, use_container_width=True, hide_index=True)
st.download_button(
    label="Download .csv file",
    help="Download the above shown data as a .csv file",
    data=data.to_csv(index=False),
    file_name="iceberg_melt_rates_by_system.csv",
    mime="text/csv",
)

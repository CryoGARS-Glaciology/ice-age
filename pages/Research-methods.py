import streamlit as st
from graphviz import Digraph

from modules.styling import centered_image

st.title("ICE-AGE Research Methods")
st.markdown(
    "This page describes how the imagery underlying ICE-AGE is turned into the "
    "iceberg outlines, volumes, and melt rates shown in the Iceberg Viewer and "
    "Statistics Dashboard."
)

with st.expander("How was ICE-AGE created?", expanded=True):
    st.markdown(
        "ICE-AGE initially reflects results from very high-resolution satellite "
        "imagery for 2011–2023. The processing pipeline can be applied to a "
        "variety of imagery types, including ArcticDEM time-stamped DEMs."
    )
    centered_image("catalog-data/images/DEM-differencing.png")
    st.info(
        "Example of high-resolution iceberg elevation observations, differenced "
        "between repeat acquisitions, used for melt rate estimates. "
        "Method: Enderlin & Hamilton (2014)."
    )

    st.markdown("Automated iceberg detection for distributions:")
    centered_image("catalog-data/images/DrJukes.png")
    st.info(
        "Learn more about iceberg fragmentation theory in "
        "[Enderlin et al. (2023)](https://doi.org/10.18739/A2SX64B7D)."
    )

    st.markdown(
        "Elevations for each iceberg are derived from stereo satellite image "
        "pairs (scene 1 / scene 2 below), which are used to generate a DEM for "
        "each acquisition date. Differencing DEMs from two dates for the same "
        "iceberg (right) isolates the elevation change used to compute melt rate."
    )
    centered_image("catalog-data/images/Aman-cool-scientist.png")

dot = Digraph()
dot.attr(rankdir="TB", bgcolor="transparent", nodesep="0.35", ranksep="0.45", splines="spline")
dot.attr(
    "node", shape="box", style="filled,rounded", fillcolor="#EAF3FA:#CFE8F5",
    gradientangle="90", color="#0047AB", penwidth="1.6",
    fontname="Helvetica", fontsize="13", fontcolor="#0B2545",
    margin="0.22,0.14",
)
dot.attr("edge", color="#0E7C9E", penwidth="1.8", arrowsize="0.85", arrowhead="vee")

# Labels wrap with \n so boxes grow to fit the text instead of clipping it.
dot.node("A", "Worldview stereo images")
dot.node("B", "DEM generation by NASA Ames\nStereo Pipeline (ASP)")
dot.node("C", "Manual iceberg tracking")
dot.node("D", "Differencing repeat DEMs")
dot.node("E", "Compute volume change")
dot.node("F", "Subtract surface melting\nfrom volume change")
dot.node("G", "Freshwater flux from\nsubmarine melting")
dot.node("H", "Melt rate =\nfreshwater flux / submerged area", fillcolor="#0047AB:#0E7C9E", fontcolor="white")
dot.edges(["AB", "BC", "CD", "DE", "EF", "FG", "GH"])

st.header("Processing Pipeline", divider=True)
_, flowchart_col, _ = st.columns([1, 2, 1])
with flowchart_col:
    st.graphviz_chart(dot)

st.header("References", divider=True)
st.markdown(
    "- Enderlin, E. M. and Hamilton, G. S. (2014). Estimates of iceberg submarine "
    "melting from high-resolution digital elevation models: application to Sermilik "
    "Fjord, East Greenland. *Journal of Glaciology*, 60(224), 1084–1092. "
    "[https://doi.org/10.3189/2014JoG14J085](https://doi.org/10.3189/2014JoG14J085)\n"
    "- Enderlin, E. M., Friel, A., Liu, J., and Kopera, M. (2023). Greenland ice "
    "mélange fragmentation theory curve parameters from digital elevation models "
    "(2011–2020). NSF Arctic Data Center. "
    "[https://doi.org/10.18739/A2SX64B7D](https://doi.org/10.18739/A2SX64B7D)"
)

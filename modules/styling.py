import streamlit as st

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

/* Cards used for callout content (Home, Acknowledgements, metric tiles) */
.card, .content-box {
    background-color: #EAF3FA;
    border: 1px solid #CBDCE8;
    border-left: 4px solid #0E7C9E;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin: 0.5rem 0 1rem 0;
}
.card ul, .content-box ul {
    margin-bottom: 0;
}

/* Icon + label metric tiles, e.g. Home's "Available Iceberg Metrics" */
.metric-tile {
    background-color: #EAF3FA;
    border: 1px solid #CBDCE8;
    border-top: 4px solid #0047AB;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    min-height: 130px;
    display: flex;
    flex-direction: column;
}
.metric-tile .metric-tile-icon {
    font-size: 1.6rem;
    line-height: 1;
}
.metric-tile .metric-tile-label {
    font-weight: 600;
    margin-top: 0.4rem;
    display: block;
}

/* Soft rounded frame + shadow for embedded maps (folium). Deliberately NOT
applied to .stImage img: several figures on Research-Methods already have
their own baked-in rectangular border, and rounding the CSS bounding box
on top of that clips across the image's own border, showing as a stray
dark/blue outline at the corners. */
[data-testid="stIFrame"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(20, 60, 90, 0.12);
}
</style>
"""


def resample_colors(anchors: list[str], count: int) -> list[str]:
    """
    Resample a list of anchor hex colors into exactly ``count`` evenly spaced
    hex colors, interpolating linearly in RGB between neighbouring anchors.

    Lets a chart hand a colormap's stops to a discrete (ordinal) color scale
    whose category count is driven by the data, without pulling a plotting
    library in at runtime just to sample a ramp.

    :param anchors: Ordered ``#rrggbb`` stops describing the colormap.
    :param count: Number of colors to return.

    :return:
        List of ``count`` ``#rrggbb`` strings, starting and ending on the
        first and last anchor.
    """
    if count <= 0:
        return []
    if count == 1:
        return [anchors[0]]

    channels = [
        tuple(int(anchor[index : index + 2], 16) for index in (1, 3, 5))
        for anchor in anchors
    ]

    colors = []
    for step in range(count):
        # Position along the anchor list, as a float index into `channels`.
        position = step * (len(channels) - 1) / (count - 1)
        low = int(position)
        high = min(low + 1, len(channels) - 1)
        weight = position - low
        blended = (
            round(channels[low][channel] * (1 - weight) + channels[high][channel] * weight)
            for channel in range(3)
        )
        colors.append("#{:02x}{:02x}{:02x}".format(*blended))
    return colors


def inject_global_styles() -> None:
    """
    Inject shared CSS (fonts, .card/.content-box, .metric-tile, and rounded
    image/map framing) once for the whole app.
    """
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def centered_image(path: str, caption: str = None, width: int = 650) -> None:
    """
    Render an image centered on the page at a fixed, readable width instead
    of stretching it to the full (often very wide) main-content container.
    """
    _, center, _ = st.columns([1, 3, 1])
    with center:
        st.image(path, caption=caption, width=width)


def metric_tile(icon: str, label: str) -> None:
    """
    Render a small icon + label tile (used for Home's feature/metric list).
    """
    st.markdown(
        f"""
        <div class="metric-tile">
            <span class="metric-tile-icon">{icon}</span>
            <span class="metric-tile-label">{label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

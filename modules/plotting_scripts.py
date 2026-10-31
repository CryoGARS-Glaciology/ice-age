from importlib.resources import files

import folium
from jinja2 import Template


class SiteLines(folium.MacroElement):
    """
    Highlight the lines connecting the "early" and "late" iceberg locations while
    hovering over it.

    Must be added to the feature group after the shape and line layers.
    """

    JAVASCRIPT = files("static").joinpath("highlight_lines.js").read_text()

    _template = Template(
        """
        {% macro script(this, kwargs) %}
            ({{ this.JAVASCRIPT }})({{ this._parent.get_name() }});
        {% endmacro %}
        """
    )

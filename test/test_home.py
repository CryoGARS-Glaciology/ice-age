from unittest.mock import patch

from streamlit.testing.v1 import AppTest


def test_home_shape_and_stats_button():
    """
    Verifies UI buttons on the map to link to Shapes and Statistics pages.
    """
    at = AppTest.from_file("ice_age_app.py")
    map_click_return = {
        "last_active_drawing": {
            "properties": {
                "Official_name": "Kong Oscar Glacier",
                "Glacier_ID": "KOG",
                "has_shapes": 1,
                "has_statistics": 1,
            }
        }
    }

    with patch("modules.plotting.overview_map", return_value=map_click_return):
        at.switch_page("pages/Home.py")
        at.run()

        assert "Study Sites in Greenland" in at.header[0].value
        assert "__Name__: Kong Oscar Glacier" in at.markdown[2].value

        assert at.main.children[6].children[1].button[0].label == "View Shapes"
        assert at.main.children[6].children[1].button[1].label == "Show Statistics"

        # Test Navigation Integration
        at.main.children[6].children[1].button[1].click().run()
        assert at.header[1].value == "Key Iceberg Statistics"


def test_home_no_selection_state():
    """Verify legend of map with no selection"""
    at = AppTest.from_file("ice_age_app.py")

    with patch("pages.Home.overview_map", return_value={"last_active_drawing": {}}):
        at.switch_page("pages/Home.py")
        at.run()

        assert "Select a glacier site to see options" in at.markdown[2].value

        html_elements = at.get("html")
        assert any("fa-map-marker" in h.proto.body for h in html_elements)

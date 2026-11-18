import streamlit as st


def load_css(*paths: str) -> None:
    """
    Load one or more local stylesheets from the pages folder into the page.
    """
    for path in paths:
        with open(path, "r") as f:
            st.html(f"<style>{f.read()}</style>")


def centered_image(path: str, caption: str = "", width: int = 650) -> None:
    """
    Render an image centered on the page at a fixed, readable width instead
    of stretching it to the full (often very wide) main-content container.
    """
    _, center, _ = st.columns([1, 3, 1])
    with center:
        st.image(path, caption=caption, width=width)

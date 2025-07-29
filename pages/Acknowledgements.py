import streamlit as st

st.html(
    """
    <style>
    /* Title text color */
    .stTitle {
        font-size: 2rem;
        font-weight: bold;
    }
    /* Text and links styling */
    .stMarkdown a {
        color: #4a90e2;  /* Light blue link color */
        text-decoration: none;
        font-weight: bold;
    }
    .stMarkdown a:hover {
        text-decoration: underline;
    }
    /* Image styling */
    .stImage {
        border-radius: 10px;
    }
    </style>
    """,
)

# Titles and content
st.title("🥳 Acknowledgements:")
st.info(
    "Project funding via NSF Arctic Natural Sciences awards #2052561, #2052549, #205255"
)
st.html(
    """
    <div class="card">
        <ul>
            <li><strong>Authors:</strong> Twila A. Moon, Dustin Carroll, Ellyn Enderlin, Aman KC, Alexandra Friel</li>
            <li><strong>Institutions:</strong> Boise State University, University of Colorado Boulder, San Jose State University, National Snow and Ice Data Center, Cooperative Institute for Research in Environmental Sciences, & Jet Propulsion Laboratory California Institute of Technology</li>
            <li><strong>Data Generation:</strong> Alexandra Friel, Isabella Welk, Alex Iturriria, Madelyn Woods</li>
            <li><strong>Data Visualization & Streamlit Application Development:</strong> Alexandra Friel</li>
        </ul>
    </div>
    """
)

st.title("🔮 The Future of ICE-AGE:")
st.html(
    """
    <div class="card">
        ICE-AGE is designed as a database that can grow and evolve. The full code and workflow for ICE-AGE will be publicly accessible. ICE-AGE is meant as a community resource to reduce the idea-to-research timeline for iceberg-focused research. Within our team, ICE-AGE will inform ongoing work focused on improved freshwater flux estimates for Greenland and improved representation of iceberg-derived freshwater flux in models using DEM-differenced melt rates and an iceberg melt model.
    </div>
    """
)

# Links section
st.html(
    "<h3>If you liked this ICE-AGE application, you may also be interested in: </h3>"
)
st.markdown(
    "[ICEBERGER: Interactive Tool for Iceberg Research](https://joshdata.me/iceberger.html)"
)
st.markdown(
    "[Zenodo Record - ICE-AGE Data](https://zenodo.org/records/8007035)"
)

# Sidebar with images aligned side by side
col1, col2 = st.sidebar.columns(2)

# Image for NSIDC on the left column
col1.image(
    "catalog-data/images/NSIDC.png",
    use_container_width=True,
    width=240
)

# Image for NSF on the right column
col2.image(
    "catalog-data/images/NSF.png",
    use_container_width=True,
    width=250
)

# Existing sidebar images
st.sidebar.image(
    "catalog-data/images/Institutions.png"
)
st.sidebar.image(
    "catalog-data/images/Scenic-glacier.png",
    caption="Tundra ponds form along the coast near Ilulissat, Greenland, while icebergs are visible along the horizon. Credit: Twila Moon, NSIDC"
)
st.sidebar.image(
    "catalog-data/images/Chilly-iceberg.png",
    caption="Credit: Twila Moon, NSIDC"
)

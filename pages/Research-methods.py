import streamlit as st



st.title('ICE-AGE Research Methods')
st.markdown('This page will describe the flow and methods to __________')

st.sidebar.title("Customize Map Appearance")
map_style = st.sidebar.selectbox(
    "Select Map Style", 
    options=["CartoDB positron", "CartoDB dark_matter"],
    index=0  # Default style: CartoDB positron
)

st.sidebar.image("catalog-data/images/Calving.png", caption = "An iceberg towers above the waters of Ilulissat Icefjord, after calving off of Sermeq Kujalleq, or Jakobshavn Glacier, in western Greenland. Credit: Allen Pope, NSIDC")
st.sidebar.image("catalog-data/images/Boats-n-icebergs.png", caption= "A scientific research vessel churns through the coastal waters of western Greenland, leaving an open path through small icebergs and bergy bits. Instruments deployed in the region help researchers to better understand ocean conditions and how narwhal whales use the glacial fjord environment. Credit: Twila Moon, NSIDC")


with st.expander("How was ICE-AGE created?", expanded=True):
    st.markdown("ICE-AGE will initially reflect results from very high-resolution satellite imagery for 2011-2023. The processing pipeline can be applied to a variety of imagery types, including ArcticDEM time-stamped DEMs.")
    st.image("catalog-data/images/DEM-differencing.png")
    st.info("Example of high- resolution iceberg elevation observations for melt rate estimates. Method: Enderlin & Hamilton (2014).")
    #st.markdown("ICE-AGE is based on imagery from 2011-2023 and includes ArcticDEM time-stamped DEMs. Code is available on GitHub: [GitHub link](https://doi.org/10.5281/zenodo.8011424)")

    st.markdown("Automated iceberg detection for distributions:")
    st.image("catalog-data/images/DrJukes.png")
    st.info("Learn more about iceberg fragmentation theory in [Enderlin et al. (2023)](https://doi.org/10.18739/A2SX64B7D).")


from graphviz import Digraph

# Create a Digraph object
dot = Digraph()

# Set the graph size (increase as needed)
dot.attr(size='80,100')  # Adjust the size
dot.attr(dpi='100')  # Optional: Increase resolution for better clarity

# Add nodes
dot.node('A', 'Worldview stereo images', shape='rect', style='filled', fillcolor='lightblue')
dot.node('B', 'DEMs generation by NASA Ames Stereo Pipeline (ASP)', shape='rect', style='filled', fillcolor='lightblue')
dot.node('C', 'Manual iceberg tracking', shape='rect', style='filled', fillcolor='lightblue')
dot.node('D', 'Differencing DEMs', shape='rect', style='filled', fillcolor='lightblue')
dot.node('E', 'Compute Volume Change', shape='rect', style='filled', fillcolor='lightblue')
dot.node('F', 'Subtract surface melting from volume change ', shape='rect', style='filled', fillcolor='lightblue')
dot.node('G', 'Freshwater flux from submarine melting', shape='rect', style='filled', fillcolor='lightblue')
dot.node('H', 'melt rate = freshwater flux / submerged area ', shape='rect', style='filled', fillcolor='lightblue')


dot.edges(['AB', 'BC', 'CD', 'DE', 'EF', 'FG', 'GH'])
col1 = st.container()
with col1:
    st.graphviz_chart(dot)
    st.image("catalog-data/images/Aman-cool-scientist.png", caption="Woot woot", use_container_width=True)  # Replace with your image path


st.title("Data Generation:")
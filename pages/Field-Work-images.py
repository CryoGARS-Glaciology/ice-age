import streamlit as st

from modules.styling import centered_image

st.title("Field Work")
st.markdown(
    "Photos from Greenland fieldwork and ship-based surveys that support "
    "ICE-AGE's imagery and melt-rate observations."
)

IMAGES = [
    "catalog-data/images/Calving.png",
    "catalog-data/images/Boats-n-icebergs.png",
]
CAPTIONS = [
    (
        "An iceberg towers above the waters of Ilulissat Icefjord, after "
        "calving off of Sermeq Kujalleq, or Jakobshavn Glacier, in western "
        "Greenland. Credit: Allen Pope, NSIDC"
    ),
    (
        "A scientific research vessel churns through the coastal waters of "
        "western Greenland, leaving an open path through small icebergs and "
        "bergy bits. Instruments deployed in the region help researchers "
        "better understand ocean conditions and how narwhal whales use the "
        "glacial fjord environment. Credit: Twila Moon, NSIDC"
    ),
]

for image, caption in zip(IMAGES, CAPTIONS):
    centered_image(image, caption=caption)

import streamlit as st

IMAGES = [
    "catalog-data/images/Ice-bridge.png",
    "catalog-data/images/Icebergs.png",
    "catalog-data/images/Sunset-icebergs.png",
    "catalog-data/images/Glacier-iceberg.png",
    "catalog-data/images/Swirly-iceberg.png",
    "catalog-data/images/Beautiful-icebergs.png",
    "catalog-data/images/aerial-shot.png",
    "catalog-data/images/aerial-iceborgs.png",
]
CAPTIONS = [
    "Surprising iceberg shapes drift in the coastal waters near Ilulissat, Greenland. Credit: Twila Moon, NSIDC",
    "An iceberg drifts in the sea off the coast of Ilulissat, Greenland. Credit: Twila Moon, NSIDC",
    "Icebergs crowd the waters along the northwestern Greenland coast. Credit: Twila Moon, NSIDC",
    "Iceberg in Kongsfjord, Svalbard. Credit: Allen Pope, NSIDC",
    (
        "A sculpted Iceberg drifts off of Baffin Island, Nunavut. "
        "Icebergs form when chunks of ice calve, or break off, from glaciers, ice shelves, "
        "or a larger iceberg. The North Atlantic and the cold waters surrounding Antarctica "
        "are home to most of the icebergs on Earth. Credit: Shari Fox, NSIDC"
    ),
    "Credit: Twila Moon, NSIDC",
    (
        "Low-angled sunlight illuminates Antarctica’s Matusevich Glacier in "
        "this image from September 6, 2010. The image was acquired by the "
        "Advanced Land Imager (ALI) on NASA’s Earth Observing-1 (EO-1) "
        "satellite, and it shows a deeply crevassed glacier breaking "
        "apart amid ocean waves. Credit: NASA"
    ),
    (
        "Aerial view of icebergs in the sea ice near Qaanaaq, Greenland. "
        "Icebergs form when chunks of ice calve, or break off, from "
        "glaciers, ice shelves, or a larger iceberg. The North Atlantic "
        "and the cold waters surrounding Antarctica are home to most of "
        "the icebergs on Earth.Credit: Shari Fox, NSIDC"
    ),
]

st.image(
    image=IMAGES, caption=CAPTIONS, use_container_width=True
)

import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

from modules.statistics import load_dates, load_site_names, load_statistics
from modules.data_path import FIGURE_EXPORT

# Title and introductory information
st.title('📊 Iceberg Statistics Dashboard')
st.info('Click here for the [Fjord Abbreviation List & Paired Dates](https://docs.google.com/spreadsheets/d/1kCcKqf717kK3_Xx-GDe0f61jhlUpZ5n6BN1qtiw7S4w/edit?gid=0#gid=0)')

# User interactions
with st.container():
    st.header("Filter")
    menu_col1, menu_col2 = st.columns(2)

with menu_col1:
    site_name = st.selectbox(
        "Select Site Name:",
        load_site_names(),
    )

# Construct folder and file paths
if site_name:
    dates = load_dates(site_name)

    with menu_col2:
        date_range = st.selectbox(
            "Select Date Range:",
            dates
        )

if site_name and date_range:
    csv_data, figure_data = load_statistics(site_name, date_range)

    st.write("### Iceberg Meltrate Information:")
    st.dataframe(csv_data)

    # Download option to export CSV data
    csv_data = csv_data.to_csv(index=False)
    st.download_button(
        label="Download .csv file",
        data=csv_data,
        file_name="iceberg_melt_rates.csv",
        mime="text/csv",
    )

    # Figure
    st.write("### Correlogram of Iceberg Features")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        figure_data.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax
    )
    st.pyplot(fig)

    # Save figure option
    fig.savefig(FIGURE_EXPORT)

    with open(FIGURE_EXPORT, "rb") as img_file:
        st.download_button(
            label="Download PNG image",
            data=img_file,
            file_name="correlogram.png",
            mime="image/png",
        )

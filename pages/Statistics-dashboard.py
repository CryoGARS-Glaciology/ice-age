import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Title and introductory information
st.title('📊 Iceberg Statistics Dashboard')
st.info('Click here for the [Fjord Abbreviation List & Paired Dates](https://docs.google.com/spreadsheets/d/1kCcKqf717kK3_Xx-GDe0f61jhlUpZ5n6BN1qtiw7S4w/edit?gid=0#gid=0)')

# Base directory where data is stored
base_path = "catalog-data/Melt-rates"

# User interactions
with st.container():
    st.header("Filter")
    menu_col1, menu_col2, menu_col3 = st.columns(3)

with menu_col1:
    site_name = st.selectbox("Select Site Name:", ["KOG", "SEK", "ASG"], index=0)  # Default is "KOG"
with menu_col2:
    early_date = st.text_input("Enter Early Date (YYYYMMDD):", "20170515")  #Default date
with menu_col3:
    later_date = st.text_input("Enter Later Date (YYYYMMDD):", "20170611")

# Construct folder and file paths
if site_name and early_date and later_date:
    folder_path = os.path.join(base_path, site_name, f"{early_date}-{later_date}")
    csv_file_name = f"{site_name}_{early_date}-{later_date}_iceberg_meltinfo.csv"
    csv_file_path = os.path.join(folder_path, csv_file_name)

    # Check if file exists
    if os.path.exists(csv_file_path):
        # Load the CSV file
        df = pd.read_csv(csv_file_path)
        st.write("### Iceberg Meltrate Information:")
        st.dataframe(df)

        # Add a save button for the melt rate table
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download .csv file",
            data=csv_data,
            file_name="iceberg_melt_rates.csv",
            mime="text/csv",
        )

        # Drop unwanted columns
        unwanted_columns = ['X_i', 'Y_i', 'TimeSeparation', 'VerticalAdjustment_i', 'VerticalAdjustment_f', 'Density_i', 'Density_f']
        df = df.drop(columns=[col for col in unwanted_columns if col in df.columns])

        # Display the correlogram
        st.write("### Correlogram of Iceberg Features")
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(df.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        st.pyplot(fig)

        # Save correlogram as an image
        correlogram_path = "catalog-data/correlogram.png"
        fig.savefig(correlogram_path)

        # Add a save button for the correlogram
        with open(correlogram_path, "rb") as img_file:
            st.download_button(
                label="Download as a .png image",
                data=img_file,
                file_name="correlogram.png",
                mime="image/png",
            )
    else:
        # Clear the GIF if file not found, but show error
        st.error("🚫 CSV file not found. Please check your inputs! 🚫")
else:
    st.warning("⚠️ Please provide all inputs: Site Name, Early Date, and Later Date.")

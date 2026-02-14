import duckdb

MELT_RATES_TABLE = "meltrates"
SITE_COLUMNS = {
    "Site Abbreviation": "Glacier_ID",  # Matches the ID from the Locations CSV
    "Date start (YYYYMMDD)": "Date_start",
    "Date end (YYYYMMDD)": "Date_end",
}
DATA_COLUMNS = {
    "X (m)": "X",
    "Y (m)": "Y",
    "Z (m)": "Z",
    "Density (kg m^-3)": "Density",
    "Volume start (m^3)": "Volume_Start",
    "Volume end (m^3)": "Volume_End",
    "Vertical coreg. start (m)": "Vertical_Coregistration_start",
    "Vertical coreg. end (m)": "Vertical_Coregistration_end",
    "dZ mean (m)": "dZ_mean",
    "dZ st.dev. (m)": "dZ_std",
    "dVdt mean (m^3 d^-1)": "dVdt_mean",
    "dVdt uncert. (m^3 d^-1)": "dVdt_uncertainty",
    "Draft mean (m)": "Draft_mean",
    "Draft range (m)": "Draft_range",
    "Surface Area mean (m^2)": "Surface_Area_mean",
    "Surface Area range (m^2)": "Surface_Area_range",
    "Submerged Area mean (m^2)": "Submerged_Area_mean",
    "Submerged Area uncert. (m^2)": "Submerged_Area_uncertainty",
    "MeltRate (m d^-1)": "Melt_Rate",
    "MeltRate uncert. (m d^-1)": "Melt_Rate_uncertainty",
}
CREATE_TABLE_SQL = (
    f"""
        "Site" VARCHAR,
    CREATE TABLE IF NOT EXISTS {MELT_RATES_TABLE} (
        "Date_start" DATE,
        "Date_end" DATE,
    """
    + ", ".join([f'"{key}" DECIMAL' for key in DATA_COLUMNS.values()])
    + ");"
)


def add_meltrates(db_path, csv_dir):
    with duckdb.connect(db_path) as connection:
        connection.execute(f"DROP TABLE IF EXISTS {MELT_RATES_TABLE};")
        connection.execute(CREATE_TABLE_SQL)
        for file in csv_dir.glob("*.csv"):
            connection.sql(
                f"""INSERT INTO {MELT_RATES_TABLE}  
                SELECT * FROM read_csv("{file}", dateformat="%Y%m%d")"""
            )

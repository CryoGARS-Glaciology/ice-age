from pathlib import Path

from database.imports import add_locations, add_meltrates, add_shapefiles

CATALOG_DATA = Path(__file__).parent.parent / "catalog-data"
DB_PATH = CATALOG_DATA / "ice_age.duckdb"

LOCATIONS_CSV = CATALOG_DATA / "Glacier-Locations.csv"
# Iceberg Viewer
SHAPEFILES_DIR = CATALOG_DATA / "iceberg-shapefiles"
# Statistics Dashboard
MELT_RATES_CSV_DIR = CATALOG_DATA / "meltrates-csv"


def populate_db():
    """
    Populate the database with raw CSV data. This will wipe out any existing tables
    and replace with the contents from the CSV and shape files.
    """
    add_meltrates(DB_PATH, MELT_RATES_CSV_DIR)
    add_locations(DB_PATH, LOCATIONS_CSV)
    add_shapefiles(DB_PATH, SHAPEFILES_DIR)


if __name__ == "__main__":
    populate_db()

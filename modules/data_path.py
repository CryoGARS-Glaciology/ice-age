# All paths to data sources are defined here

from pathlib import Path

# Map on Home showing all locations
# Required columns: 'LAT', 'LON', 'Official_n', 'Glacier_ID'
GLACIER_LOCATIONS_CSV = "catalog-data/Glacier-Locations.csv"
# Statistics Dashboard
MELT_RATES_DIR = Path("catalog-data/Melt-rates")
FIGURE_EXPORT = "catalog-data/correlogram.png"

NATURAL_EARTH_ZIP = "catalog-data/ne_110m_admin_0_countries.zip"
SHAPEFILE_CATALOG_DIR = "catalog-data/iceberg-shapefiles"

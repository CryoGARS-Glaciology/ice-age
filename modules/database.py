import ibis

DB_PATH = "catalog-data/ice_age.duckdb"
CONNECTION = ibis.duckdb.connect(DB_PATH, read_only=True, extensions=["spatial"])

LOCATIONS = CONNECTION.table("locations")
MELT_RATES = CONNECTION.table("meltrates")

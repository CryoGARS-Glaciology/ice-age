import duckdb

LOCATIONS_TABLE = "locations"


def add_locations(db_path, csv_file):
    with duckdb.connect(db_path) as connection:
        connection.load_extension("spatial")
        connection.execute(f"DROP TABLE IF EXISTS {LOCATIONS_TABLE};")
        connection.sql(
            f"""CREATE TABLE {LOCATIONS_TABLE} AS 
            SELECT Glacier_ID, Official_n as Official_name, ST_Point(LON, LAT) as geometry 
            FROM read_csv("{csv_file}")"""
        )

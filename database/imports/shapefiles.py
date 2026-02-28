import os

import duckdb

SHAPE_TABLE = "shapes"


def add_shapefiles(db_path, shapefiles):
    connection = duckdb.connect(db_path)
    connection.sql("LOAD spatial;")

    shp_files = [str(f) for f in shapefiles.glob("*.shp")]

    # Combine
    union_query = " UNION ALL BY NAME ".join(
        [
            f"SELECT SiteID, IcebergID, "
            f"strptime(DATE, '%Y%m%d')::DATE AS Date, "
            f"'{os.path.basename(f)}' AS filename, "
            "* EXCLUDE (SiteID, IcebergID, Date) "
            f"FROM ST_Read('{f}')"
            for f in shp_files
        ]
    )

    # Execute and sort
    connection.sql(
        f"""
        CREATE OR REPLACE TABLE {SHAPE_TABLE} AS 
        SELECT * FROM ({union_query})
        ORDER BY ST_Hilbert(geom)
    """
    )

    connection.sql(
        f"""
        CREATE INDEX IF NOT EXISTS geom_idx 
        ON {SHAPE_TABLE} USING RTREE (geom)
    """
    )

    connection.close()

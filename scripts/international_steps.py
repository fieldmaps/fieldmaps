"""Write catalog/international/ from a fieldmaps/international run with --debug."""

from pathlib import Path

import compare
import duckdb

BUILD = compare.ROOT.parent / "international"
CATALOG = compare.ROOT / "catalog" / "international"
DEBUG = BUILD / "tmp" / "debug"
OPTS = "COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2"
WORLD = "ST_MakeEnvelope(-180, -90, 180, 90)"
CLIP = (
    f"ST_SetCRS(ST_ReducePrecision(ST_Intersection({{}}, {WORLD}), 1e-9), 'OGC:CRS84')"
)
# Collection name, its source file, and the columns it keeps.
STEPS = {
    "lsib": (
        DEBUG / "_03_build" / "lsib_00.parquet",
        CLIP.format("ST_LineMerge(geom)"),
    ),
    "template": (
        BUILD / "inputs" / "adm0_lines.parquet",
        CLIP.format("ST_LineMerge(geom)"),
    ),
    "points": (
        DEBUG / "osm" / "_03_build" / "points_00.parquet",
        "id, " + CLIP.format("geom"),
    ),
    "areas": (
        DEBUG / "osm" / "_03_build" / "voronoi_00.parquet",
        "id, " + CLIP.format("geom"),
    ),
}
COVERAGES = ("areas",)


def output(collection: str) -> Path:
    """Return a collection's GeoParquet path."""
    return CATALOG / collection / f"{collection}.parquet"


def build() -> None:
    """Rewrite the collections when stale and fail on invalid geometry or coverage."""
    inputs = [Path(__file__)] + [src for src, _ in STEPS.values()]
    if all(compare.fresh(output(c), inputs) for c in STEPS):
        return
    conn = duckdb.connect()
    conn.execute("LOAD spatial; SET geometry_always_xy = true;")
    conn.execute(f"SET threads = {compare.THREADS};")
    for collection, (src, columns) in STEPS.items():
        query = f"SELECT * FROM (SELECT {columns} AS geom FROM '{src}')"
        if collection != "points":
            query += " WHERE NOT ST_IsEmpty(geom)"
        conn.execute(f"COPY ({query}) TO '{output(collection)}' ({OPTS})")
    for collection in STEPS:
        invalid = conn.execute(
            f"SELECT count(*) FILTER (NOT ST_IsValid(geom)) FROM '{output(collection)}'"
        ).fetchall()[0][0]
        if invalid:
            msg = f"{collection}: {invalid} invalid geometries"
            raise ValueError(msg)
    for collection in COVERAGES:
        bad = conn.execute(
            f"SELECT ST_CoverageInvalidEdges_Agg(geom, 1e-8) IS NOT NULL "
            f"FROM '{output(collection)}'"
        ).fetchall()[0][0]
        if bad:
            msg = f"{collection}: invalid coverage"
            raise ValueError(msg)
    conn.close()


if __name__ == "__main__":
    build()

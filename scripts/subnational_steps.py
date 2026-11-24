"""Write catalog/subnational/ from a topo-tools edge-extend --debug run per country."""

from pathlib import Path

import compare
import duckdb

FIELDMAPS = compare.ROOT.parent
CATALOG = compare.ROOT / "catalog" / "subnational"
WORK = compare.ROOT / "tmp" / "subnational"
SOURCE = FIELDMAPS / "subnational" / "catalog"
ADM0 = (
    (FIELDMAPS / "international" / "catalog" / "odbl" / "humanitarian")
    / "adm0-polygons"
    / "adm0_polygons.parquet"
)
# Admin level of each country's source, which names its published polygons.
COUNTRIES = {"NIC": 2, "TZA": 2, "KEN": 2}
OPTS = "COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2"
WORLD = "ST_MakeEnvelope(-180, -90, 180, 90)"
CLIP = f"ST_SetCRS(ST_Intersection(geom, {WORLD}), 'OGC:CRS84')"
# Collection name and the topo-tools intermediate it is read from.
STEPS = {
    "original": "01",
    "outlines": "02",
    "points": "03b",
    "cells": "04_tmp2",
    "dissolved": "04",
    "extended": "05",
}
COLLECTIONS = [*STEPS, "clipped", "adm0", "mismatch"]
COVERAGES = ("original", "cells", "extended", "clipped")


def output(collection: str) -> Path:
    """Return a collection's GeoParquet path."""
    return CATALOG / collection / f"{collection}.parquet"


def original(iso3: str) -> Path:
    """Return the country's original polygons from fieldmaps/subnational."""
    iso = iso3.lower()
    return SOURCE / "source" / iso / f"{iso}_original.parquet"


def finer(iso3: str) -> list[str]:
    """Return the original's columns for levels finer than the country's level."""
    names = duckdb.sql(f"DESCRIBE FROM '{original(iso3)}'").fetchall()
    level = COUNTRIES[iso3]
    return [n for n, *_ in names if n[:3] == "adm" and int(n[3]) > level]


def source(iso3: str) -> Path:
    """Return the edge-extend input, dissolved to the country's level when needed."""
    if not finer(iso3):
        return original(iso3)
    return WORK / iso3.lower() / f"{iso3.lower()}_adm{COUNTRIES[iso3]}.parquet"


def dissolve(iso3: str) -> None:
    """Dissolve the original to the country's level unless the result is fresh."""
    out = source(iso3)
    if out == original(iso3) or compare.fresh(out, [original(iso3)]):
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    drop = ", ".join([*finer(iso3), "geometry"])
    conn = duckdb.connect()
    conn.execute("LOAD spatial; SET geometry_always_xy = true;")
    conn.execute(
        f"COPY (SELECT * EXCLUDE ({drop}), ST_CoverageUnion_Agg(geometry) AS geometry "
        f"FROM '{original(iso3)}' GROUP BY ALL) TO '{out}' ({OPTS})"
    )
    conn.close()


def published(iso3: str, level: int) -> Path:
    """Return the country's published polygons at its source level."""
    return SOURCE / "iso3" / iso3.lower() / f"adm{level}_polygons.parquet"


def step(iso3: str, name: str) -> Path:
    """Return one topo-tools intermediate for a country."""
    iso = iso3.lower()
    return WORK / iso / "work" / f"{source(iso3).stem}_parquet_{name}.parquet"


def extend(iso3: str) -> None:
    """Run edge-extend --debug for a country unless its intermediates are fresh."""
    dissolve(iso3)
    if compare.fresh(step(iso3, "05"), [source(iso3)]):
        return
    work = WORK / iso3.lower()
    (work / "work").mkdir(parents=True, exist_ok=True)
    compare.topo_tools(
        "edge-extend",
        source(iso3),
        work / "extended.parquet",
        "--debug",
        "--tmp-dir",
        work / "work",
    )


def union(selects: dict[str, str]) -> str:
    """Join one SELECT per country, each tagged with its iso3."""
    return " UNION ALL ".join(
        f"SELECT '{iso3}' AS iso3, {select}" for iso3, select in selects.items()
    )


def copy(conn: duckdb.DuckDBPyConnection, query: str, collection: str) -> None:
    """Write a query with clipped geometry to a collection."""
    cols = {"mismatch": "iso3, kind"}.get(collection, "iso3")
    if collection in STEPS:
        cols = "iso3, fid"
    sql = f"SELECT {cols}, {CLIP} AS geom FROM ({query})"
    conn.execute(f"COPY ({sql}) TO '{output(collection)}' ({OPTS})")


def write(conn: duckdb.DuckDBPyConnection) -> None:
    """Write every collection."""
    for collection, name in STEPS.items():
        query = union({i: f"fid, geom FROM '{step(i, name)}'" for i in COUNTRIES})
        copy(conn, query, collection)
    copy(
        conn,
        union(
            {
                i: f"geometry AS geom FROM '{published(i, lvl)}'"
                for i, lvl in COUNTRIES.items()
            }
        ),
        "clipped",
    )
    isos = ", ".join(f"'{i}'" for i in COUNTRIES)
    adm0 = f"SELECT iso3, geometry AS geom FROM '{ADM0}' WHERE iso3 IN ({isos})"
    copy(conn, adm0, "adm0")
    original = union({i: f"geom FROM '{step(i, '01')}'" for i in COUNTRIES})
    copy(
        conn,
        f"""
        WITH o AS (SELECT iso3, ST_Union_Agg(geom) AS g FROM ({original}) GROUP BY 1),
        a AS (SELECT iso3, ST_Union_Agg(geom) AS g FROM ({adm0}) GROUP BY 1)
        SELECT iso3, 'gap' AS kind, ST_Difference(a.g, o.g) AS geom
        FROM o JOIN a USING (iso3)
        UNION ALL SELECT iso3, 'spill', ST_Difference(o.g, a.g)
        FROM o JOIN a USING (iso3)
        """,
        "mismatch",
    )


def check(conn: duckdb.DuckDBPyConnection) -> None:
    """Raise on invalid geometry, a missing country, or a broken coverage."""
    for collection in COLLECTIONS:
        invalid, countries = conn.execute(
            "SELECT count(*) FILTER (NOT ST_IsValid(geom)), count(DISTINCT iso3) "
            f"FROM '{output(collection)}'"
        ).fetchall()[0]
        if invalid or countries != len(COUNTRIES):
            msg = f"{collection}: {invalid} invalid, {countries} countries"
            raise ValueError(msg)
    for collection in COVERAGES:
        bad = conn.execute(
            f"SELECT list(iso3) FROM (SELECT iso3 FROM '{output(collection)}' "
            "GROUP BY iso3 HAVING ST_CoverageInvalidEdges_Agg(geom, 1e-8) IS NOT NULL)"
        ).fetchall()[0][0]
        if bad:
            msg = f"{collection}: invalid coverage in {bad}"
            raise ValueError(msg)


def build() -> None:
    """Refresh each country's intermediates, then rewrite stale collections."""
    for iso3 in COUNTRIES:
        extend(iso3)
    inputs = [Path(__file__), ADM0]
    inputs += [step(i, name) for i in COUNTRIES for name in STEPS.values()]
    inputs += [published(i, level) for i, level in COUNTRIES.items()]
    if all(compare.fresh(output(c), inputs) for c in COLLECTIONS):
        return
    for collection in COLLECTIONS:
        output(collection).parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect()
    conn.execute("LOAD spatial; SET geometry_always_xy = true;")
    conn.execute(f"SET threads = {compare.THREADS};")
    write(conn)
    check(conn)
    conn.close()


if __name__ == "__main__":
    build()

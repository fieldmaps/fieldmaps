"""Download each comparison source and write its polygons to catalog/compare/."""

import os
import re
import shutil
import urllib.request
from pathlib import Path
from zipfile import ZipFile

import duckdb
from tenacity import retry, stop_after_attempt, wait_exponential

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog" / "compare"
DOWNLOAD = ROOT / "tmp" / "compare" / "download"
THREADS = max(1, (os.cpu_count() or 2) // 2)
WORLD = "ST_MakeEnvelope(-180, -90, 180, 90)"
CLIP = (
    "ST_Multi(ST_CollectionExtract("
    f"ST_Intersection(ST_MakeValid(geometry), {WORLD}), 3))"
)
OPTS = "FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2"
FIELDMAPS_URL = "https://data.source.coop/fieldmaps/international/odbl/humanitarian/adm0-polygons/adm0_polygons.parquet"
WP_URL = "https://data.geodata.state.gov/WorldPolygons.zip"


@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=2, max=60), reraise=True)
def fetch(url: str, dest: Path) -> Path:
    """Download ``url`` to ``dest`` unless it is already there."""
    if dest.exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})  # noqa: S310
    with urllib.request.urlopen(request) as r, part.open("wb") as f:  # noqa: S310
        shutil.copyfileobj(r, f, 1 << 20)
    part.rename(dest)
    return dest


def fieldmaps(_: duckdb.DuckDBPyConnection) -> str:
    """FieldMaps humanitarian ADM0 polygons."""
    path = fetch(FIELDMAPS_URL, DOWNLOAD / "fieldmaps" / "adm0_polygons.parquet")
    return f"SELECT iso3, adm0_name AS name, geometry FROM read_parquet('{path}')"


def wp(conn: duckdb.DuckDBPyConnection) -> str:
    """US State Department World Polygons, full-resolution layer."""
    out = DOWNLOAD / "wp"
    gpkg = next(out.rglob("WorldPolygons*.gpkg"), None)
    if gpkg is None:
        # The outer zip also holds a Deflate64 hash file that zipfile can't read.
        with ZipFile(fetch(WP_URL, out / "WorldPolygons.zip")) as z:
            inner = next(
                n for n in z.namelist() if re.search(r"WorldPolygon[^/]*\.zip$", n)
            )
            z.extract(inner, out)
        with ZipFile(out / inner) as z:
            z.extractall(out)
        gpkg = next(out.rglob("WorldPolygons*.gpkg"))
    layer = next(
        name
        for (name,) in conn.execute(
            f"SELECT UNNEST(layers).name FROM ST_Read_Meta('{gpkg}')"
        ).fetchall()
        if re.fullmatch(r"DoS_WP_\d+_\d+", name)
    )
    return (
        "SELECT GENC_3 AS iso3, WP_Name AS name, geom AS geometry "
        f"FROM ST_Read('{gpkg}', layer='{layer}')"
    )


SOURCES = {"fieldmaps": fieldmaps, "wp": wp}


def prepare() -> None:
    """Write catalog/compare/<source>-polygons/<source>_polygons.parquet per source."""
    conn = duckdb.connect()
    conn.execute(
        f"LOAD spatial; SET geometry_always_xy = true; SET threads = {THREADS}"
    )
    for source, query in SOURCES.items():
        out = CATALOG / f"{source}-polygons" / f"{source}_polygons.parquet"
        out.parent.mkdir(parents=True, exist_ok=True)
        conn.execute(f"""
            COPY (
                SELECT iso3, name, ST_SetCRS(CASE
                    WHEN ST_XMin(geometry) >= -180 AND ST_XMax(geometry) <= 180
                        AND ST_YMin(geometry) >= -90 AND ST_YMax(geometry) <= 90
                    THEN geometry
                    ELSE {CLIP}
                END, 'OGC:CRS84') AS geometry
                FROM ({query(conn)})
                ORDER BY ST_Hilbert(geometry, ST_Extent({WORLD}))
            ) TO '{out}' ({OPTS})
        """)
        print(out.relative_to(ROOT))  # noqa: T201


if __name__ == "__main__":
    prepare()

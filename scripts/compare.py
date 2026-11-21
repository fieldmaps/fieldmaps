"""Download each comparison source and write its polygons to catalog/compare/."""

import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from email.utils import formatdate, parsedate_to_datetime
from http import HTTPStatus
from pathlib import Path
from subprocess import run
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
TOPO_TOOLS = Path(sys.executable).parent / "topo-tools"
WP_URL = "https://data.geodata.state.gov/WorldPolygons.zip"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30), reraise=True)
def download(url: str, dest: Path) -> bool:
    """Download ``url`` to ``dest`` if the server copy is newer; return if it did."""
    headers = {"User-Agent": "Mozilla/5.0"}
    if dest.exists():
        headers["If-Modified-Since"] = formatdate(dest.stat().st_mtime, usegmt=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    request = urllib.request.Request(url, headers=headers)  # noqa: S310
    try:
        with urllib.request.urlopen(request, timeout=60) as r, part.open("wb") as f:  # noqa: S310
            shutil.copyfileobj(r, f, 1 << 20)
            modified = r.headers.get("Last-Modified")
    except urllib.error.HTTPError as e:
        if e.code == HTTPStatus.NOT_MODIFIED:
            return False
        raise
    part.replace(dest)
    # If-Modified-Since then compares against the server's clock, not our download time.
    if modified:
        t = parsedate_to_datetime(modified).timestamp()
        os.utime(dest, (t, t))
    return True


def refresh(url: str, dest: Path, cached: Path | None) -> bool:
    """Run ``download``, reusing ``cached`` when the host is unavailable."""
    try:
        return download(url, dest)
    except OSError as e:
        if cached is None:
            raise
        print(f"{url} unavailable ({e}), reusing {cached.relative_to(ROOT)}")  # noqa: T201
        return False


def wp(conn: duckdb.DuckDBPyConnection) -> str:
    """US State Department World Polygons, full-resolution layer."""
    out = DOWNLOAD / "wp"
    archive = out / "WorldPolygons.zip"
    gpkg = next(out.rglob("WorldPolygons*.gpkg"), None)
    if refresh(WP_URL, archive, gpkg) or gpkg is None:
        for p in out.iterdir():
            if p != archive:
                shutil.rmtree(p) if p.is_dir() else p.unlink()
        # The outer zip also holds a Deflate64 hash file that zipfile can't read.
        with ZipFile(archive) as z:
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
        "SELECT * EXCLUDE geom, geom AS geometry "
        f"FROM ST_Read('{gpkg}', layer='{layer}')"
    )


SOURCES = {"wp": wp}


def prepare() -> None:
    """Write catalog/compare/<source>-polygons/<source>_polygons.parquet per source."""
    conn = duckdb.connect()
    conn.execute(
        f"LOAD spatial; SET geometry_always_xy = true; SET threads = {THREADS}"
    )
    work = ROOT / "tmp" / "compare"
    for source, query in SOURCES.items():
        out = CATALOG / f"{source}-polygons" / f"{source}_polygons.parquet"
        out.parent.mkdir(parents=True, exist_ok=True)
        clipped = work / f"{source}_polygons.parquet"
        conn.execute(f"""
            COPY (
                SELECT * REPLACE (ST_SetCRS(CASE
                    WHEN ST_XMin(geometry) >= -180 AND ST_XMax(geometry) <= 180
                        AND ST_YMin(geometry) >= -90 AND ST_YMax(geometry) <= 90
                    THEN geometry
                    ELSE {CLIP}
                END, 'OGC:CRS84') AS geometry)
                FROM ({query(conn)})
            ) TO '{clipped}' ({OPTS})
        """)
        cleaned = work / f"{source}_polygons_cleaned.parquet"
        issues = work / f"{source}_polygons_issues.parquet"
        run(
            [
                TOPO_TOOLS,
                "topo-clean",
                clipped,
                cleaned,
                "--issues-file",
                issues,
                "--threads",
                str(THREADS),
            ],
            check=True,
        )
        conn.execute(f"""
            COPY (
                SELECT * FROM '{cleaned}'
                ORDER BY ST_Hilbert(geometry, ST_Extent({WORLD}))
            ) TO '{out}' ({OPTS})
        """)
        print(out.relative_to(ROOT))  # noqa: T201


if __name__ == "__main__":
    prepare()

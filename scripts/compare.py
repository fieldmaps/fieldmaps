"""Download comparison sources, write their polygons, lines and Voronoi layers."""

import argparse
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable
from email.utils import formatdate, parsedate_to_datetime
from http import HTTPStatus
from pathlib import Path
from subprocess import CalledProcessError, run
from zipfile import ZipFile

import duckdb
from tenacity import retry, stop_after_attempt, wait_exponential

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog" / "compare"
WORK = ROOT / "tmp" / "compare"
DOWNLOAD = WORK / "download"
THREADS = max(1, (os.cpu_count() or 2) // 2)
WORLD = "ST_MakeEnvelope(-180, -90, 180, 90)"
CLIP = (
    "ST_Multi(ST_CollectionExtract("
    f"ST_Intersection(ST_MakeValid(geometry), {WORLD}), 3))"
)
HILBERT = f"ORDER BY ST_Hilbert(geometry, ST_Extent({WORLD}))"
OPTS = "FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2"
TOPO_TOOLS = Path(sys.executable).parent / "topo-tools"
WP_URL = "https://data.geodata.state.gov/WorldPolygons.zip"
OVERTURE = "2026-11-18.0"
S3 = f"s3://overturemaps-us-west-2/release/{OVERTURE}"
# Overture files territories such as Greenland or Réunion as dependencies.
OVERTURE_FILES = (
    ("division_area", "country"),
    ("division_area", "dependency"),
    ("division_boundary", "country"),
)
FILES = {
    "lsib": "https://data.geodata.state.gov/LSIB.gpkg",
    "wb": "https://datacatalogfiles.worldbank.org/ddh-published/0038272/3/DR0096331/"
    "World%20Bank%20Official%20Boundaries%20%28Parquet%29/"
    "World%20Bank%20Official%20Boundaries%20-%20Admin%200_all_layers.parquet",
    "gaul": "https://storage.googleapis.com/fao-maps-catalog-data/boundaries/GAUL_2025_L1.zip",
    "gadm": "https://geodata.ucdavis.edu/gadm/gadm4.1/gadm_410-levels.zip",
    "cgaz": "https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/main/"
    "releaseData/CGAZ/geoBoundariesCGAZ_ADM0.gpkg",
    "ne": "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip",
}
SAVE_AS = {"wb": "wb_admin0_all_layers.parquet"}
# Overture's columns, name and code first; topo-clean and edge-extend move geometry.
OVERTURE_COLUMNS = (
    "name, iso3, country, region, subtype, class, admin_level, is_land, "
    "is_territorial, id, division_id, version, theme, type, geometry"
)
COLUMNS = {"overture": OVERTURE_COLUMNS}
# Country code and name column of each prepared polygon layer.
FIELDS = {
    "wp": ("GENC_3", "WP_Name"),
    "overture": ("iso3", "name"),
    "wb": ("ISO_A3", "NAM_0"),
    "gaul": ("ISO3_CODE", "GAUL0_NAME"),
    "gadm": ("iso3", "COUNTRY"),
    "cgaz": ("shapeGroup", "shapeName"),
    "ne": ("ADM0_A3", "NAME"),
}


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


def fetch_file(source: str) -> None:
    """Refresh one file source, extracting it when it is a zip."""
    url = FILES[source]
    dest = DOWNLOAD / source / SAVE_AS.get(source, url.rsplit("/", 1)[-1])
    if refresh(url, dest, dest if dest.exists() else None) and dest.suffix == ".zip":
        with ZipFile(dest) as z:
            z.extractall(dest.parent)


def fetch_wp() -> None:
    """Refresh World Polygons and LSIB."""
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
    fetch_file("lsib")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30), reraise=True)
def fetch_overture() -> None:
    """Copy each of the pinned Overture release's OVERTURE_FILES from S3."""
    conn = duckdb.connect()
    conn.execute(f"""
        INSTALL httpfs; LOAD httpfs; SET threads = {THREADS};
        CREATE SECRET (TYPE s3, PROVIDER config, REGION 'us-west-2');
    """)
    for kind, subtype in OVERTURE_FILES:
        dest = DOWNLOAD / "overture" / f"{kind}_{subtype}_{OVERTURE}.parquet"
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        part = dest.with_suffix(".part")
        conn.execute(f"""
            COPY (
                SELECT * FROM read_parquet('{S3}/theme=divisions/type={kind}/*.parquet')
                WHERE subtype = '{subtype}'
            ) TO '{part}' (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 15)
        """)
        part.replace(dest)


FETCH: dict[str, Callable[[], None]] = {
    "wp": fetch_wp,
    "overture": fetch_overture,
    **{s: lambda s=s: fetch_file(s) for s in ("wb", "gaul", "gadm", "cgaz", "ne")},
}


def wp_query(conn: duckdb.DuckDBPyConnection) -> str:
    """US State Department World Polygons, full-resolution layer."""
    gpkg = next((DOWNLOAD / "wp").rglob("WorldPolygons*.gpkg"))
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


def overture_query(_: duckdb.DuckDBPyConnection) -> str:
    """Overture land country and dependency areas, ISO3 from the ISO2 `country`."""
    return f"""
        SELECT coalesce(a.names.common['en'], a.names.primary) AS name,
            CASE a.country WHEN 'TW' THEN 'TWN' WHEN 'XK' THEN 'XKX'
                WHEN 'CP' THEN 'CPT' WHEN 'XE' THEN 'BES' WHEN 'XS' THEN 'BES'
                WHEN 'XJ' THEN 'SJM' ELSE r.iso3 END AS iso3,
            a.country, a.region, a.subtype, a.class, a.admin_level, a.is_land,
            a.is_territorial, a.id, a.division_id, a.version, a.theme, a.type,
            a.geometry
        FROM read_parquet([
            '{DOWNLOAD}/overture/division_area_country_{OVERTURE}.parquet',
            '{DOWNLOAD}/overture/division_area_dependency_{OVERTURE}.parquet'
        ]) AS a
        LEFT JOIN read_csv('{ROOT}/scripts/iso2_iso3.csv') AS r
            ON r.iso2 = a.country
        WHERE a.class = 'land'
    """


def wb_query(_: duckdb.DuckDBPyConnection) -> str:
    """World Bank Official Boundaries, Admin 0, every row as published."""
    return f"SELECT * FROM '{DOWNLOAD}/wb/{SAVE_AS['wb']}'"


def gaul_query(_: duckdb.DuckDBPyConnection) -> str:
    """FAO GAUL 2025, L1 dissolved on its country-level columns."""
    cols = "ISO3_CODE, MAP_CODE, GAUL0_CODE, GAUL0_NAME, CONTINENT"
    return f"""
        SELECT {cols}, ST_Union_Agg(geom) AS geometry
        FROM ST_Read('{DOWNLOAD}/gaul/gaul_2025_l1.shp') GROUP BY {cols}
    """


def gadm_query(_: duckdb.DuckDBPyConnection) -> str:
    """GADM 4.1 ADM_0 without the Caspian Sea, Kosovo coded XKX in iso3."""
    return f"""
        SELECT * EXCLUDE geom,
            CASE GID_0 WHEN 'XKO' THEN 'XKX' ELSE GID_0 END AS iso3,
            geom AS geometry
        FROM ST_Read('{DOWNLOAD}/gadm/gadm_410-levels.gpkg', layer='ADM_0')
        WHERE GID_0 != 'XCA'
    """


def cgaz_query(_: duckdb.DuckDBPyConnection) -> str:
    """GeoBoundaries CGAZ ADM0."""
    gpkg = DOWNLOAD / "cgaz" / "geoBoundariesCGAZ_ADM0.gpkg"
    return f"SELECT * EXCLUDE geom, geom AS geometry FROM ST_Read('{gpkg}')"


def ne_query(_: duckdb.DuckDBPyConnection) -> str:
    """Natural Earth 10m admin 0 countries."""
    shp = DOWNLOAD / "ne" / "ne_10m_admin_0_countries.shp"
    return f"SELECT * EXCLUDE geom, geom AS geometry FROM ST_Read('{shp}')"


QUERIES: dict[str, Callable[[duckdb.DuckDBPyConnection], str]] = {
    "wp": wp_query,
    "overture": overture_query,
    "wb": wb_query,
    "gaul": gaul_query,
    "gadm": gadm_query,
    "cgaz": cgaz_query,
    "ne": ne_query,
}
SOURCES = list(QUERIES)


def connect() -> duckdb.DuckDBPyConnection:
    """Open DuckDB with spatial, lon/lat axis order and the thread cap."""
    conn = duckdb.connect()
    conn.execute(
        f"LOAD spatial; SET geometry_always_xy = true; SET threads = {THREADS}"
    )
    return conn


def output(source: str, kind: str) -> Path:
    """Catalog path of one layer, e.g. catalog/compare/ne-lines/ne_lines.parquet."""
    return CATALOG / f"{source}-{kind}" / f"{source}_{kind}.parquet"


def files(*paths: Path) -> Iterable[Path]:
    """Every file in ``paths``, walking directories."""
    for p in paths:
        yield from (f for f in p.rglob("*") if f.is_file()) if p.is_dir() else [p]


def fresh(out: Path, inputs: Iterable[Path]) -> bool:
    """Whether ``out`` exists and is at least as new as every input."""
    return out.exists() and all(
        out.stat().st_mtime >= p.stat().st_mtime for p in inputs
    )


def topo_tools(command: str, src: Path, dest: Path, *args: str | Path) -> None:
    """Run one topo-tools command with the thread cap."""
    run([TOPO_TOOLS, command, src, dest, *args, "--threads", str(THREADS)], check=True)


def publish(conn: duckdb.DuckDBPyConnection, query: str, out: Path) -> None:
    """Write ``query`` to ``out`` in Hilbert order."""
    out.parent.mkdir(parents=True, exist_ok=True)
    conn.execute(f"COPY (SELECT * FROM ({query}) {HILBERT}) TO '{out}' ({OPTS})")


def prepare(source: str) -> None:
    """Clip a source to world bounds, then topo-clean it as one layer."""
    conn = connect()
    clipped = WORK / f"{source}_polygons.parquet"
    conn.execute(f"""
        COPY (
            SELECT * REPLACE (ST_SetCRS(CASE
                WHEN ST_XMin(geometry) >= -180 AND ST_XMax(geometry) <= 180
                    AND ST_YMin(geometry) >= -90 AND ST_YMax(geometry) <= 90
                THEN geometry
                ELSE {CLIP}
            END, 'OGC:CRS84') AS geometry)
            FROM ({QUERIES[source](conn)})
        ) TO '{clipped}' ({OPTS})
    """)
    cleaned = WORK / f"{source}_polygons_cleaned.parquet"
    issues = WORK / f"{source}_polygons_issues.parquet"
    topo_tools("topo-clean", clipped, cleaned, "--issues-file", issues)
    order = COLUMNS.get(source, "*")
    publish(conn, f"SELECT {order} FROM '{cleaned}'", output(source, "polygons"))


def lines(source: str) -> None:
    """Write boundary lines: the source's own where it publishes them, else derived."""
    conn = connect()
    out = output(source, "lines")
    if source == "wp":
        publish(
            conn,
            f"""
            SELECT * EXCLUDE geom,
                CASE STATUS
                    WHEN 'International Boundary' THEN 'international'
                    WHEN 'Other Line of International Separation' THEN 'armistice'
                    WHEN 'Special Line' THEN 'special'
                END AS line_type,
                ST_SetCRS(geom, 'OGC:CRS84') AS geometry
            FROM ST_Read('{DOWNLOAD}/lsib/LSIB.gpkg')
            """,
            out,
        )
        return
    if source == "overture":
        publish(
            conn,
            f"""
            SELECT
                CASE WHEN is_disputed THEN 'armistice' ELSE 'international' END
                    AS line_type,
                is_disputed, country, region, subtype, class, admin_level, is_land,
                is_territorial, id, version, theme, type, geometry
            FROM '{DOWNLOAD}/overture/division_boundary_country_{OVERTURE}.parquet'
            WHERE class = 'land'
            """,
            out,
        )
        return
    code, name = FIELDS[source]
    lookup = WORK / f"{source}_units_lookup.parquet"
    conn.execute(f"""
        COPY (
            SELECT 'U' || row_number() OVER () AS unit, "{code}" AS code,
                "{name}" AS name, geometry
            FROM '{output(source, "polygons")}'
        ) TO '{lookup}' ({OPTS})
    """)
    # package-lines detects levels from unique names, and some sources repeat names.
    units = WORK / f"{source}_units.parquet"
    conn.execute(f"""
        COPY (SELECT unit AS adm0_pcode, unit AS adm0_name, geometry FROM '{lookup}')
        TO '{units}' ({OPTS})
    """)
    derived = WORK / f"{source}_lines_all.parquet"
    topo_tools("package-lines", units, derived)
    publish(
        conn,
        f"""
        SELECT a.code AS a_code, a.name AS a_name, b.code AS b_code, b.name AS b_name,
            'international' AS line_type, l.geometry
        FROM '{derived}' AS l
        JOIN '{lookup}' AS a ON a.unit = l.a_code
        JOIN '{lookup}' AS b ON b.unit = l.b_code
        WHERE l.adm_lvl = 0
        """,
        out,
    )


def voronoi(source: str) -> None:
    """Extend the polygons over water and gaps with topo-tools edge-extend."""
    extended = WORK / f"{source}_voronoi.parquet"
    topo_tools("edge-extend", output(source, "polygons"), extended)
    order = COLUMNS.get(source, "*")
    publish(connect(), f"SELECT {order} FROM '{extended}'", output(source, "voronoi"))


def inputs(stage: str, source: str) -> list[Path]:
    """Files a stage reads for one source."""
    if stage == "prepare":
        dirs = [DOWNLOAD / source] + (
            [DOWNLOAD / "ref"] if source == "overture" else []
        )
        return [*files(*dirs)]
    if stage == "lines" and source == "wp":
        return [DOWNLOAD / "lsib" / "LSIB.gpkg"]
    if stage == "lines" and source == "overture":
        return [DOWNLOAD / "overture" / f"division_boundary_country_{OVERTURE}.parquet"]
    return [output(source, "polygons")]


STAGES: dict[str, Callable[[str], None]] = {
    "prepare": prepare,
    "lines": lines,
    "voronoi": voronoi,
}
OUTPUT_KIND = {"prepare": "polygons", "lines": "lines", "voronoi": "voronoi"}


def build(
    stages: Iterable[str] = STAGES,
    sources: Iterable[str] = SOURCES,
    *,
    force: bool = False,
) -> list[str]:
    """Run each stage for each source, skipping fresh outputs; return what failed."""
    failed = []
    for stage in stages:
        for source in sources:
            out = output(source, OUTPUT_KIND[stage])
            if not force and fresh(out, inputs(stage, source)):
                continue
            try:
                STAGES[stage](source)
            except (CalledProcessError, duckdb.Error, StopIteration) as e:
                failed.append(f"{stage} {source}: {e}")
                print(f"failed: {stage} {source}: {e}")  # noqa: T201
                continue
            print(out.relative_to(ROOT))  # noqa: T201
    return failed


def main() -> None:
    """Run the stages and sources given on the command line, or all of them."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["download", *STAGES], action="append")
    parser.add_argument("--source", choices=SOURCES, action="append")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    sources = args.source or SOURCES
    stages = args.stage or ["download", *STAGES]
    if "download" in stages:
        for source in sources:
            FETCH[source]()
    failed = build([s for s in stages if s != "download"], sources, force=args.force)
    if failed:
        sys.exit("\n".join(failed))


if __name__ == "__main__":
    main()

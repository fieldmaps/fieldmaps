"""Write each source's subnational polygons for the explorer, clipped as published."""

import os
from pathlib import Path
from zipfile import ZipFile

import compare
import duckdb
from tenacity import retry, stop_after_attempt, wait_exponential

ROOT = compare.ROOT
CATALOG = ROOT / "catalog" / "explore"
# Kept apart from compare's downloads, which compare treats as its inputs.
DOWNLOAD = ROOT / "tmp" / "explore" / "download"
GADM = compare.DOWNLOAD / "gadm" / "gadm_410-levels.gpkg"
GAUL_L1 = compare.DOWNLOAD / "gaul" / "gaul_2025_l1.shp"
THREADS = os.cpu_count() or 1
WB = (
    "https://datacatalogfiles.worldbank.org/ddh-published/0038272/3/DR0096331/"
    "World%20Bank%20Official%20Boundaries%20%28Parquet%29/"
    "World%20Bank%20Official%20Boundaries%20-%20Admin%20{n}.parquet"
)
CGAZ = (
    "https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/main/"
    "releaseData/CGAZ/geoBoundariesCGAZ_ADM{n}.gpkg"
)
FILES = {
    DOWNLOAD / "gaul" / "GAUL_2025_L2.zip": "https://storage.googleapis.com/"
    "fao-maps-catalog-data/boundaries/GAUL_2025_L2.zip",
    DOWNLOAD / "ne" / "ne_10m_admin_1_states_provinces.zip": "https://naciscdn.org/"
    "naturalearth/10m/cultural/ne_10m_admin_1_states_provinces.zip",
    **{
        DOWNLOAD / "cgaz" / f"geoBoundariesCGAZ_ADM{n}.gpkg": CGAZ.format(n=n)
        for n in (1, 2)
    },
    **{DOWNLOAD / "wb" / f"wb_admin{n}.parquet": WB.format(n=n) for n in (1, 2)},
}
OVERTURE_SUBTYPES = ("region", "county", "localadmin")


def overture(subtype: str) -> Path:
    """Local copy of one Overture division_area subtype."""
    return DOWNLOAD / "overture" / f"division_area_{subtype}_{compare.OVERTURE}.parquet"


def fetch() -> None:
    """Download each missing input, extracting zips next to them."""
    for dest, url in FILES.items():
        if not dest.exists():
            compare.download(url, dest)
        if dest.suffix == ".zip":
            with ZipFile(dest) as z:
                if not all((dest.parent / n).exists() for n in z.namelist()):
                    z.extractall(dest.parent)
    # GADM levels and GAUL L1 are compare's own inputs.
    for source, path in (("gadm", GADM), ("gaul", GAUL_L1)):
        if not path.exists():
            compare.fetch_file(source)
    fetch_overture()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30), reraise=True)
def fetch_overture() -> None:
    """Copy each missing Overture subtype from S3."""
    missing = [s for s in OVERTURE_SUBTYPES if not overture(s).exists()]
    if not missing:
        return
    conn = duckdb.connect()
    conn.execute(f"""
        INSTALL httpfs; LOAD httpfs; SET threads = {THREADS};
        CREATE SECRET (TYPE s3, PROVIDER config, REGION 'us-west-2');
    """)
    for subtype in missing:
        dest = overture(subtype)
        dest.parent.mkdir(parents=True, exist_ok=True)
        part = dest.with_suffix(".part")
        conn.execute(f"""
            COPY (
                SELECT * FROM read_parquet(
                    '{compare.S3}/theme=divisions/type=division_area/*.parquet')
                WHERE subtype = '{subtype}' AND class = 'land'
            ) TO '{part}' (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 15)
        """)
        part.replace(dest)


def read(path: Path, layer: str | None = None) -> str:
    """Every column of a GDAL-readable layer, its geometry as ``geometry``."""
    opt = f", layer='{layer}'" if layer else ""
    return f"SELECT * EXCLUDE geom, geom AS geometry FROM ST_Read('{path}'{opt})"


def overture_level(subtype: str) -> str:
    """One Overture subtype, its nested columns swapped for a single ``name``."""
    return f"""
        SELECT * EXCLUDE (geometry, names, sources, bbox),
            coalesce(names.common['en'], names.primary) AS name, geometry
        FROM '{overture(subtype)}'
    """


# Each layer keyed {source}-adm{level}: the file it reads, and its query.
LEVELS: dict[str, tuple[Path, str]] = {
    **{f"gadm-adm{n}": (GADM, read(GADM, f"ADM_{n}")) for n in range(1, 5)},
    **{
        f"gaul-adm{n}": (p, read(p))
        for n, p in ((1, GAUL_L1), (2, DOWNLOAD / "gaul" / "gaul_2025_l2.shp"))
    },
    **{
        f"cgaz-adm{n}": (p, read(p))
        for n in (1, 2)
        for p in [DOWNLOAD / "cgaz" / f"geoBoundariesCGAZ_ADM{n}.gpkg"]
    },
    **{
        f"wb-adm{n}": (p, f"SELECT * FROM '{p}'")
        for n in (1, 2)
        for p in [DOWNLOAD / "wb" / f"wb_admin{n}.parquet"]
    },
    **{
        f"overture-adm{n}": (overture(s), overture_level(s))
        for n, s in enumerate(OVERTURE_SUBTYPES, 1)
    },
    "ne-adm1": (
        p := DOWNLOAD / "ne" / "ne_10m_admin_1_states_provinces.shp",
        read(p),
    ),
}


def output(layer: str) -> Path:
    """Catalog path of one layer, e.g. explore/ne-adm1-polygons/ne_adm1_polygons."""
    return CATALOG / f"{layer}-polygons" / f"{layer.replace('-', '_')}_polygons.parquet"


def build() -> None:
    """Download missing inputs, then write each stale layer clipped to world bounds."""
    fetch()
    conn = compare.connect()
    conn.execute(f"SET threads = {THREADS}")
    for layer, (src, query) in LEVELS.items():
        out = output(layer)
        if compare.fresh(out, [src]):
            continue
        compare.publish(
            conn,
            f"""
            SELECT * REPLACE (ST_SetCRS(CASE
                WHEN ST_XMin(geometry) >= -180 AND ST_XMax(geometry) <= 180
                    AND ST_YMin(geometry) >= -90 AND ST_YMax(geometry) <= 90
                THEN geometry
                ELSE {compare.CLIP}
            END, 'OGC:CRS84') AS geometry)
            FROM ({query})
            """,
            out,
        )
        print(out.relative_to(ROOT))  # noqa: T201

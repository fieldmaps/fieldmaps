"""Compare land boundaries on OSM land, and each source's islands in other cells."""

import json
import os
import sys
import urllib.parse
import urllib.request
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile

import compare
import compare_attributes
import compare_review
import duckdb
from tenacity import retry, stop_after_attempt, wait_exponential

THREADS = compare.THREADS
# An island gets no dot within this many of its widths of a larger island in its item.
REACH = 5
VERTICES = 256
KM2 = "ST_Area_Spheroid({}) / 1e6"
# Row slices per thread, so the largest geometries don't queue behind each other.
SLICES = 4 * THREADS
LAND_URL = "https://osmdata.openstreetmap.de/download/land-polygons-complete-4326.zip"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# Scarborough Shoal and Minerva Reefs: mapped as reefs, so absent from OSM land.
OSM_REEFS = {"way": (43145194, 43145209), "relation": (18554868,)}
OSM_DIR = compare.DOWNLOAD / "osm"
OSM_LAND = compare.WORK / "osm_land.parquet"
FIELDMAPS_LINES = (
    "https://data.source.coop/fieldmaps/international/odbl/humanitarian/"
    "adm0-lines/adm0_lines.parquet"
)
SOURCES = sorted(compare_attributes.POLYGONS)
POLYGONS = compare_attributes.POLYGONS
VORONOI = {s: compare.output(s, "voronoi") for s in SOURCES}
LINES = [FIELDMAPS_LINES, *(compare.output(s, "lines") for s in compare.SOURCES)]
# Per source, a key unique per feature and shared by its polygon and Voronoi rows.
ENTITY = {
    # adm0_id ends in its release date; dropping it keeps keys stable across releases.
    "fieldmaps": "regexp_replace(adm0_id, '-[0-9]{8}$', '')",
    "wp": "fid_orig",
    "overture": "id",
    "wb": "concat_ws('|', ISO_A3, WB_A3, NAM_0, SOV_ISO_A3, WB_STATUS)",
    "gaul": "concat_ws('|', GAUL0_CODE, MAP_CODE, ISO3_CODE, GAUL0_NAME)",
    "gadm": "GID_0",
    "cgaz": "fid_orig",
    "ne": "ADM0_A3 || '|' || NAME",
}
DB = compare.WORK / "differences.duckdb"
PARTIAL = compare.WORK / "differences.partial"
OUT = compare.CATALOG / "differences"
DOTS = compare.CATALOG / "differences-dots"
PILOT = compare.WORK / "pilot"
WORLD = compare.WORLD
# Clips only rows past the world bounds, keeping their dimension and multi-ness.
WORLD_CLIP = f"""CASE
    WHEN ST_IsEmpty(geometry) OR (
        ST_XMin(geometry) >= -180 AND ST_XMax(geometry) <= 180
        AND ST_YMin(geometry) >= -90 AND ST_YMax(geometry) <= 90
    ) THEN geometry
    ELSE (SELECT CASE WHEN starts_with(ST_GeometryType(geometry)::VARCHAR, 'MULTI')
        THEN ST_Multi(g) ELSE g END
        FROM (SELECT ST_CollectionExtract(ST_Intersection(
            ST_MakeValid(geometry), {WORLD}), ST_Dimension(geometry) + 1) AS g))
    END"""


def _log(msg: str) -> None:
    print(msg, flush=True)  # noqa: T201


def _bbox() -> str | None:
    return os.getenv("DIFF_BBOX")


def _out(name: str) -> Path:
    """Output path, under tmp/compare/pilot for a DIFF_BBOX run."""
    final = {
        "differences.parquet": OUT / "differences.parquet",
        "items.json": OUT / "items.json",
        "differences_dots.parquet": DOTS / "differences_dots.parquet",
    }[name]
    path = PILOT / name if _bbox() else final
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _write(conn: duckdb.DuckDBPyConnection, query: str, out: Path) -> None:
    """Write ``query`` to ``out`` as clipped, Hilbert-sorted GeoParquet."""
    conn.execute(f"""
        COPY (SELECT * FROM (
            SELECT * REPLACE (ST_SetCRS({WORLD_CLIP}, 'OGC:CRS84') AS geometry)
            FROM ({query})) {compare.HILBERT}) TO '{out}' ({compare.OPTS})""")
    n, crs, x0, y0, x1, y1 = conn.execute(f"""
        SELECT count(*), any_value(ST_CRS(geometry)), min(ST_XMin(geometry)),
            min(ST_YMin(geometry)), max(ST_XMax(geometry)), max(ST_YMax(geometry))
        FROM read_parquet('{out}')""").fetchall()[0]
    if n and (crs != "OGC:CRS84" or x0 < -180 or y0 < -90 or x1 > 180 or y1 > 90):  # noqa: PLR2004
        msg = f"{out.name}: CRS {crs}, bbox {x0, y0, x1, y1}"
        raise ValueError(msg)
    _log(f"{out.name}: {n} rows")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30), reraise=True)
def _reefs() -> None:
    """Write the ``OSM_REEFS`` features with their geometry to ``reefs.json``."""
    ids = "".join(f"{t}(id:{','.join(map(str, v))});" for t, v in OSM_REEFS.items())
    # Overpass answers 406 to browser-like user agents.
    body = urllib.parse.urlencode({"data": f"[out:json][timeout:60];({ids});out geom;"})
    request = urllib.request.Request(
        OVERPASS_URL, body.encode(), {"User-Agent": "fieldmaps-compare"}
    )
    with urllib.request.urlopen(request, timeout=120) as r:  # noqa: S310
        text = r.read().decode()
    found = {(e["type"], e["id"]) for e in json.loads(text)["elements"]}
    expected = {(t, i) for t, v in OSM_REEFS.items() for i in v}
    if found != expected:
        msg = f"Overpass reefs missing: {sorted(expected - found)}"
        raise ValueError(msg)
    (OSM_DIR / "reefs.json").write_text(text)


def download() -> None:
    """Refresh OSM land polygons and the reefs OSM leaves out of them."""
    archive = OSM_DIR / "land-polygons-complete-4326.zip"
    if compare.download(LAND_URL, archive) or not next(
        OSM_DIR.rglob("land_polygons.shp"), None
    ):
        with ZipFile(archive) as z:
            z.extractall(OSM_DIR)
    if not (OSM_DIR / "reefs.json").exists():
        _reefs()


def osm_land(conn: duckdb.DuckDBPyConnection) -> None:
    """Write OSM land polygons plus the reefs to ``osm_land.parquet``."""
    shp = next(OSM_DIR.rglob("land_polygons.shp"))
    rows = [
        (
            e["type"],
            e["id"],
            [
                "LINESTRING("
                + ", ".join(f"{p['lon']} {p['lat']}" for p in ring["geometry"])
                + ")"
                for ring in ([e] if e["type"] == "way" else e["members"])
            ],
        )
        for e in json.loads((OSM_DIR / "reefs.json").read_text())["elements"]
    ]
    conn.execute("""
        CREATE OR REPLACE TABLE reef_rings
            (osm_type VARCHAR, osm_id BIGINT, rings VARCHAR[])""")
    conn.executemany("INSERT INTO reef_rings VALUES (?, ?, ?)", rows)
    conn.execute(f"""
        CREATE OR REPLACE TABLE reefs AS
        SELECT osm_type, osm_id, ST_BuildArea(ST_Collect(
            list_transform(rings, lambda x: ST_GeomFromText(x)))) AS geom
        FROM reef_rings;
        CREATE OR REPLACE TABLE osm_shp AS SELECT geom FROM ST_Read('{shp}')""")
    touching = conn.execute("""
        SELECT list(r.osm_type || ' ' || r.osm_id) FROM reefs r JOIN osm_shp l
          ON ST_Intersects(r.geom, l.geom)""").fetchall()[0][0]
    if touching:
        msg = f"OSM reefs intersect OSM land: {touching}"
        raise ValueError(msg)
    _write(
        conn,
        """SELECT row_number() OVER () AS fid, geom AS geometry FROM (
            SELECT geom FROM osm_shp UNION ALL SELECT geom FROM reefs)""",
        OSM_LAND,
    )
    conn.execute("DROP TABLE osm_shp; DROP TABLE reefs; DROP TABLE reef_rings")


def _step(conn: duckdb.DuckDBPyConnection, name: str, sql: str) -> None:
    start = perf_counter()
    conn.execute(sql)
    _log(f"{name}: {perf_counter() - start:.0f}s")


def _parallel(conn: duckdb.DuckDBPyConnection, statements: list[str]) -> None:
    """Run ``statements`` side by side, each on its own cursor."""
    with ThreadPoolExecutor(THREADS) as pool:
        list(pool.map(lambda sql: conn.cursor().execute(sql), statements))


def _columns(source: str) -> str:
    """Select a source's entity, code and name columns."""
    c = compare_attributes.COLUMNS[source]
    return f"""coalesce(({ENTITY[source]})::VARCHAR, '') AS entity,
        ({c["code"]})::VARCHAR AS code, ({c["tile"]})::VARCHAR AS name"""


def _chunks(conn: duckdb.DuckDBPyConnection, name: str, table: str, src: str) -> None:
    """Write ``src``'s rows to ``table``, subdivided, with envelopes, slice by slice."""
    start = perf_counter()
    # One statement over a few hundred large rows would run on one thread.
    conn.execute(f"""
        CREATE OR REPLACE TABLE chunk_rows AS
        SELECT *, row_number() OVER (ORDER BY ST_NPoints(geom) DESC) % {SLICES} AS slice
        FROM ({src});
        CREATE OR REPLACE TABLE {table} AS
        SELECT * EXCLUDE slice, geom AS env FROM chunk_rows LIMIT 0
    """)
    _parallel(
        conn,
        [
            f"""INSERT INTO {table} BY NAME
            SELECT * EXCLUDE (geom, part, slice), part AS geom,
                ST_Envelope(part) AS env
            FROM (SELECT *, unnest(ST_Dump(ST_Subdivide(geom, {VERTICES}))).geom AS part
                FROM chunk_rows WHERE slice = {i})"""
            for i in range(SLICES)
        ],
    )
    conn.execute("DROP TABLE chunk_rows")
    _log(f"{name}: {perf_counter() - start:.0f}s")


def _land(conn: duckdb.DuckDBPyConnection) -> None:
    """Split OSM land into land chunks crossed by any line and whole islands."""
    land = f"read_parquet('{OSM_LAND}')"
    if bbox := _bbox():
        land = f"""(SELECT fid, ST_CollectionExtract(ST_Intersection(geometry,
            ST_MakeEnvelope({bbox})), 3) AS geometry FROM {land}
            WHERE ST_Intersects(geometry, ST_MakeEnvelope({bbox})))"""
    _step(
        conn,
        "land",
        f"""CREATE OR REPLACE TABLE land AS
        SELECT fid, geometry AS geom, ST_Envelope(geometry) AS env,
               {KM2.format("geometry")} AS km2
        FROM {land} WHERE NOT ST_IsEmpty(geometry)""",
    )
    lines = " UNION ALL ".join(
        f"SELECT geometry AS geom FROM read_parquet('{p}')" for p in LINES
    )
    _chunks(conn, "segments", "segs", lines)
    _step(
        conn,
        "candidates",
        """CREATE OR REPLACE TABLE candidates AS
        SELECT DISTINCT l.fid FROM land l JOIN segs s ON ST_Intersects(l.env, s.env)""",
    )
    _chunks(
        conn,
        "candidate chunks",
        "chunks",
        "SELECT fid, geom FROM land JOIN candidates USING (fid)",
    )
    _step(
        conn,
        "crossed",
        """CREATE OR REPLACE TABLE crossed AS
        SELECT DISTINCT c.fid FROM chunks c JOIN segs s
          ON ST_Intersects(c.env, s.env) AND ST_Intersects(c.geom, s.geom)""",
    )
    conn.execute(f"""
        CREATE OR REPLACE TABLE chunks AS
        SELECT row_number() OVER () AS chunk, *, {KM2.format("geom")} AS km2
        FROM chunks WHERE fid IN (SELECT fid FROM crossed);
        CREATE OR REPLACE TABLE islands AS
        SELECT fid, km2, ST_PointOnSurface(geom) AS pt FROM land
        WHERE fid NOT IN (SELECT fid FROM crossed);
    """)
    n = conn.execute(
        "SELECT (SELECT count(*) FROM crossed), (SELECT count(*) FROM islands)"
    ).fetchall()[0]
    _log(f"land: {n[0]} crossed polygons, {n[1]} islands")


def _polygons(conn: duckdb.DuckDBPyConnection) -> None:
    """Load every source's polygon parts and each entity's area."""
    conn.execute("""
        CREATE OR REPLACE TABLE polygon_parts (source VARCHAR, entity VARCHAR,
            code VARCHAR, name VARCHAR, geom GEOMETRY, env GEOMETRY)
    """)
    start = perf_counter()
    _parallel(
        conn,
        [
            f"""INSERT INTO polygon_parts
            SELECT *, ST_Envelope(geom) FROM (
                SELECT '{s}', {_columns(s)}, unnest(ST_Dump(geometry)).geom AS geom
                FROM read_parquet('{POLYGONS[s]}'))"""
            for s in SOURCES
        ],
    )
    _log(f"polygon parts: {perf_counter() - start:.0f}s")
    _step(
        conn,
        "polygon areas",
        """CREATE OR REPLACE TABLE polygon_areas AS
        SELECT source, code, name, sum(ST_Area_Spheroid(geom)) AS m2
        FROM polygon_parts GROUP BY ALL""",
    )


def _assign(conn: duckdb.DuckDBPyConnection) -> None:
    """Clip land chunks to every source's cells and put each island in one cell."""
    cells = " UNION ALL ".join(
        f"""SELECT '{s}' AS source, {_columns(s)}, geometry AS geom
        FROM read_parquet('{VORONOI[s]}')"""
        for s in SOURCES
    )
    _chunks(conn, "cells", "cells", cells)
    conn.execute("""
        CREATE OR REPLACE TABLE entities AS
        SELECT DISTINCT source, entity, code, name FROM cells
    """)
    # A chunk inside a cell stays as it is, which spares every overlay it enters.
    _step(
        conn,
        "pieces",
        f"""CREATE OR REPLACE TABLE pieces AS
        SELECT source, chunk, entity, whole, geom, CASE WHEN whole THEN chunk_km2
                ELSE {KM2.format("geom")} END AS km2,
            ST_XMin(geom) AS x0, ST_YMin(geom) AS y0,
            ST_XMax(geom) AS x1, ST_YMax(geom) AS y1
        FROM (
            SELECT *, CASE WHEN whole THEN chunk_geom ELSE ST_CollectionExtract(
                    ST_Intersection(chunk_geom, cell_geom), 3) END AS geom
            FROM (
                SELECT c.source, k.chunk, c.entity, k.km2 AS chunk_km2,
                    k.geom AS chunk_geom, c.geom AS cell_geom,
                    ST_Covers(c.geom, k.geom) AS whole
                FROM chunks k JOIN cells c
                  ON ST_Intersects(k.env, c.env) AND ST_Intersects(k.geom, c.geom)))
        """,
    )
    _polygons(conn)
    _step(
        conn,
        "islands placed",
        """CREATE OR REPLACE TABLE placed AS
        SELECT c.source, i.fid, min(c.entity) AS entity
        FROM islands i JOIN cells c ON ST_Intersects(i.pt, c.geom)
        GROUP BY c.source, i.fid""",
    )


def _overlay(conn: duckdb.DuckDBPyConnection) -> None:
    """Overlay every source pair's pieces and islands, then mutual best matches."""
    # Pieces of one chunk overlap only if their boxes do, and a whole piece cuts
    # nothing, so two whole pieces just name their chunk.
    _step(
        conn,
        "overlay",
        f"""CREATE OR REPLACE TABLE overlay AS
        SELECT a, b, a_entity, b_entity, chunk,
            coalesce(known, {KM2.format("geom")}) AS km2, geom
        FROM (
            SELECT pa.source AS a, pb.source AS b, pa.entity AS a_entity,
                pb.entity AS b_entity, pa.chunk,
                CASE WHEN pa.whole THEN pb.km2 WHEN pb.whole THEN pa.km2 END AS known,
                CASE WHEN pa.whole AND pb.whole THEN NULL
                    WHEN pa.whole THEN pb.geom WHEN pb.whole THEN pa.geom
                    ELSE ST_CollectionExtract(ST_Intersection(pa.geom, pb.geom), 3)
                    END AS geom
            FROM pieces pa JOIN pieces pb ON pa.chunk = pb.chunk
                AND pa.source < pb.source AND pa.x0 <= pb.x1 AND pb.x0 <= pa.x1
                AND pa.y0 <= pb.y1 AND pb.y0 <= pa.y1)
        WHERE geom IS NULL OR NOT ST_IsEmpty(geom)""",
    )
    conn.execute("""
        CREATE OR REPLACE TABLE island_pairs AS
        SELECT pa.source AS a, pb.source AS b, i.fid, pa.entity AS a_entity,
               pb.entity AS b_entity, i.km2
        FROM islands i JOIN placed pa USING (fid) JOIN placed pb USING (fid)
        WHERE pa.source < pb.source;
        CREATE OR REPLACE TABLE weights AS
        SELECT a, b, a_entity, b_entity, sum(km2) AS km2 FROM (
            SELECT a, b, a_entity, b_entity, km2 FROM overlay
            UNION ALL SELECT a, b, a_entity, b_entity, km2 FROM island_pairs)
        GROUP BY ALL;
        CREATE OR REPLACE TABLE matches AS
        WITH codes AS (
            SELECT source, entity, upper(code) AS code FROM entities
            WHERE coalesce(code, '') <> ''
            QUALIFY count(*) OVER (PARTITION BY source, upper(code)) = 1)
        -- A code held by one entity in each source pairs them, whatever the overlap.
        SELECT w.*, coalesce(ca.code = cb.code, false)
            OR (km2 = max(km2) OVER (PARTITION BY a, b, a_entity)
                AND km2 = max(km2) OVER (PARTITION BY a, b, b_entity)) AS mutual
        FROM weights w
        LEFT JOIN codes ca ON ca.source = w.a AND ca.entity = w.a_entity
        LEFT JOIN codes cb ON cb.source = w.b AND cb.entity = w.b_entity;
    """)
    _land_patches(conn)
    _parts(conn)


def _named(side: str) -> str:
    return f"""LEFT JOIN entities {side}e
        ON {side}e.source = d.{side} AND {side}e.entity = d.{side}_entity"""


PAIR_COLUMNS = """d.a || '|' || d.b AS pair, d.a, d.b, d.a_entity, ae.code AS a_code,
    ae.name AS a_name, d.b_entity, be.code AS b_code, be.name AS b_name"""
# A patch shows in the source whose entity has no mutual match in the other.
SIDE = """CASE WHEN pa.entity IS NULL AND pb.entity IS NOT NULL THEN 'a'
    WHEN pb.entity IS NULL AND pa.entity IS NOT NULL THEN 'b' ELSE 'both' END"""


def _sided() -> str:
    return " ".join(
        f"""LEFT JOIN paired p{x} ON p{x}.a = d.a AND p{x}.b = d.b
            AND p{x}.side = '{x}' AND p{x}.entity = d.{x}_entity"""
        for x in "ab"
    )


def _land_patches(conn: duckdb.DuckDBPyConnection) -> None:
    """Split the land each pair's entities don't share into patches."""
    conn.execute("""
        CREATE OR REPLACE TABLE paired AS
        SELECT DISTINCT a, b, 'a' AS side, a_entity AS entity FROM matches WHERE mutual
        UNION SELECT DISTINCT a, b, 'b', b_entity FROM matches WHERE mutual
    """)
    _step(
        conn,
        "land patches",
        f"""CREATE OR REPLACE TABLE land_diff AS
        SELECT {PAIR_COLUMNS}, {SIDE} AS side, {KM2.format("geom")} AS km2, geom FROM (
            SELECT a, b, a_entity, b_entity, unnest(ST_Dump(g)).geom AS geom FROM (
                SELECT a, b, a_entity, b_entity,
                    ST_Union_Agg(coalesce(o.geom, k.geom)) AS g
                FROM overlay o JOIN matches m USING (a, b, a_entity, b_entity)
                LEFT JOIN chunks k USING (chunk)
                WHERE NOT m.mutual GROUP BY ALL)) d {_named("a")} {_named("b")}
        {_sided()}""",
    )


def _parts(conn: duckdb.DuckDBPyConnection) -> None:
    """Each source's polygon parts off crossed land, placed in every source's cells."""
    bbox = _bbox()
    within = f"WHERE ST_Intersects(env, ST_MakeEnvelope({bbox}))" if bbox else ""
    conn.execute(f"""
        CREATE OR REPLACE TABLE parts AS
        SELECT row_number() OVER () AS pid, source, entity, geom, env
        FROM polygon_parts {within}
    """)
    # Only parts whose box meets crossed land need subdividing to test them.
    _step(
        conn,
        "near parts",
        """CREATE OR REPLACE TABLE near_parts AS
        SELECT DISTINCT p.pid FROM parts p JOIN chunks c
            ON ST_Intersects(p.env, c.env)""",
    )
    _chunks(
        conn,
        "part chunks",
        "part_bits",
        "SELECT pid, geom FROM parts WHERE pid IN (SELECT pid FROM near_parts)",
    )
    _step(
        conn,
        "island parts",
        f"""CREATE OR REPLACE TABLE part_land AS
        SELECT DISTINCT b.pid FROM part_bits b JOIN chunks c
            ON ST_Intersects(b.env, c.env) AND ST_Intersects(b.geom, c.geom);
        CREATE OR REPLACE TABLE island_parts AS
        SELECT pid, source, entity, {KM2.format("geom")} AS km2,
            ST_PointOnSurface(geom) AS pt, geom, env
        FROM parts WHERE pid NOT IN (SELECT pid FROM part_land);
        DROP TABLE part_bits; DROP TABLE parts""",
    )
    _step(
        conn,
        "parts placed",
        """CREATE OR REPLACE TABLE part_cells AS
        SELECT c.source, p.pid, min(c.entity) AS entity
        FROM island_parts p JOIN cells c ON ST_Intersects(p.pt, c.geom)
        GROUP BY c.source, p.pid""",
    )
    # A part's own source holds it by its polygon, whatever its cell says.
    conn.execute("""
        CREATE OR REPLACE TABLE part_placed AS
        SELECT c.* FROM part_cells c JOIN island_parts p USING (pid)
        WHERE c.source <> p.source
        UNION ALL SELECT source, pid, entity FROM island_parts;
        DROP TABLE part_cells
    """)


def _patches(conn: duckdb.DuckDBPyConnection) -> None:
    """Unshared land per pair, and islands in zones where both sources draw islands."""
    # A zone is where one source's cell overlaps another's cell of a different entity.
    conn.execute("""
        CREATE OR REPLACE TABLE patches AS
        WITH island AS (
            SELECT least(p.source, o.source) AS a, greatest(p.source, o.source) AS b,
                CASE WHEN p.source < o.source THEN 'a' ELSE 'b' END AS side,
                CASE WHEN p.source < o.source THEN p.entity ELSE o.entity END
                    AS a_entity,
                CASE WHEN p.source < o.source THEN o.entity ELSE p.entity END
                    AS b_entity,
                r.item, p.km2, p.geom
            FROM item_parts r JOIN island_parts p USING (pid)
            JOIN part_placed o ON o.pid = p.pid AND o.source <> p.source
            JOIN clusters cp ON cp.source = p.source AND cp.entity = p.entity
            JOIN clusters co ON co.source = o.source AND co.entity = o.entity
            WHERE cp.cluster <> co.cluster),
        zones AS (
            SELECT a, b, a_entity, b_entity FROM island
            GROUP BY ALL HAVING count(DISTINCT side) = 2)
        SELECT pair, 'land' AS type, side, item, a_entity, b_entity, a_code, a_name,
                b_code, b_name, km2, geom::GEOMETRY AS geometry
        FROM land_review
        UNION ALL
        SELECT d.a || '|' || d.b, 'island', d.side, d.item, d.a_entity, d.b_entity,
               ae.code, ae.name, be.code, be.name, d.km2, d.geom::GEOMETRY
        FROM island d SEMI JOIN zones z USING (a, b, a_entity, b_entity)
        LEFT JOIN entities ae ON ae.source = d.a AND ae.entity = d.a_entity
        LEFT JOIN entities be ON be.source = d.b AND be.entity = d.b_entity
    """)


def _drop_crowded(
    conn: duckdb.DuckDBPyConnection, table: str, group: str, size: str
) -> None:
    """Delete each part of `table` within REACH widths of a larger part of its group."""
    # Groups sit side by side on x offsets, so the R-tree join never pairs two groups.
    conn.execute(f"""
        CREATE OR REPLACE TEMP TABLE boxes AS
        SELECT id, {size} AS size, (x0 + x1) / 2 AS cx, (y0 + y1) / 2 AS cy,
            greatest(x1 - x0, y1 - y0) AS w, {REACH} * w AS reach,
            x0 - reach AS bx0, y0 - reach AS by0, x1 + reach AS bx1, y1 + reach AS by1,
            dense_rank() OVER (ORDER BY {group}) * (360 + 2 * max(reach) OVER ()) AS off
        FROM {table};
        DELETE FROM {table} WHERE id IN (
            WITH pairs AS MATERIALIZED (
                SELECT s.id AS sid, s.size AS ss, b.id AS bid, b.size AS bs
                FROM boxes s JOIN boxes b ON ST_Intersects(
                    ST_MakeEnvelope(b.off + b.bx0, b.by0, b.off + b.bx1, b.by1),
                    ST_Point(s.off + s.cx, s.cy)))
            SELECT sid FROM pairs WHERE bs > ss OR (bs = ss AND bid < sid));
        DROP TABLE boxes
    """)


def _dots(conn: duckdb.DuckDBPyConnection) -> None:
    """Dot each island that is not crowded by a larger one in its item."""
    conn.execute("""
        CREATE OR REPLACE TEMP TABLE dot_islands AS
        SELECT row_number() OVER () AS id, pair, side, item, km2, geometry,
            ST_XMin(geometry) AS x0, ST_XMax(geometry) AS x1,
            ST_YMin(geometry) AS y0, ST_YMax(geometry) AS y1
        FROM patches WHERE type = 'island'
    """)
    _drop_crowded(conn, "dot_islands", "pair, side, item", "km2")
    _write(
        conn,
        """SELECT pair, side, item,
            ST_MaximumInscribedCircle(geometry).center AS geometry
        FROM dot_islands""",
        _out("differences_dots.parquet"),
    )


def _areas(conn: duckdb.DuckDBPyConnection) -> None:
    """Voronoi areas a pair assigns differently, each with its largest patch's item."""
    conn.execute("""
        CREATE OR REPLACE TABLE targets AS
        SELECT DISTINCT pair, split_part(pair, '|', 1) AS a,
            split_part(pair, '|', 2) AS b, a_entity, b_entity
        FROM patches WHERE NOT (type = 'land' AND side = 'both')
            AND a_entity IS NOT NULL AND b_entity IS NOT NULL
    """)
    _step(
        conn,
        "area overlay",
        """CREATE OR REPLACE TABLE area_parts AS
        SELECT row_number() OVER () AS id, pair, a_entity, b_entity, geom FROM (
            SELECT pair, a_entity, b_entity, unnest(ST_Dump(g)).geom AS geom FROM (
                SELECT t.pair, t.a_entity, t.b_entity, ST_Union_Agg(
                    ST_CollectionExtract(ST_Intersection(ca.geom, cb.geom), 3)) AS g
                FROM targets t
                JOIN cells ca ON ca.source = t.a AND ca.entity = t.a_entity
                JOIN cells cb ON cb.source = t.b AND cb.entity = t.b_entity
                    AND ST_Intersects(ca.env, cb.env)
                    AND ST_Intersects(ca.geom, cb.geom)
                GROUP BY ALL))""",
    )
    _step(
        conn,
        "area items",
        f"""CREATE OR REPLACE TABLE areas AS
        SELECT any_value(v.pair) AS pair, 'voronoi' AS type,
            arg_max(p.side, p.km2) AS side, arg_max(p.item, p.km2) AS item,
            arg_max(p.a_code, p.km2) AS a_code, arg_max(p.a_name, p.km2) AS a_name,
            arg_max(p.b_code, p.km2) AS b_code, arg_max(p.b_name, p.km2) AS b_name,
            {KM2.format("any_value(v.geom)")} AS km2, any_value(v.geom) AS geometry
        FROM area_parts v JOIN patches p ON p.pair = v.pair
            AND p.a_entity = v.a_entity AND p.b_entity = v.b_entity
            AND NOT (p.type = 'land' AND p.side = 'both')
            AND ST_Intersects(v.geom, p.geometry)
        GROUP BY v.id""",
    )


def _review(conn: duckdb.DuckDBPyConnection) -> None:
    """Group differences into items, then write patches, dots, areas and items."""
    compare_review.build(conn, SOURCES)
    _patches(conn)
    _areas(conn)
    lost = conn.execute("""
        SELECT count(*) FROM (
            SELECT item FROM patches WHERE NOT (type = 'land' AND side = 'both')
            UNION ALL SELECT item FROM areas)
        WHERE item IS NULL OR item NOT IN (SELECT item FROM items)""").fetchall()[0][0]
    if lost:
        msg = f"{lost} differences belong to no item"
        raise ValueError(msg)
    _dots(conn)
    _write(
        conn,
        """SELECT * EXCLUDE (a_entity, b_entity) FROM patches
        UNION ALL BY NAME SELECT * FROM areas""",
        _out("differences.parquet"),
    )
    _items(conn)


def _items(conn: duckdb.DuckDBPyConnection) -> None:
    """Write items.json, titling each item with its smallest entity's own name."""
    named = " UNION ALL ".join(
        f"SELECT item, '{s}' AS source, {s}_code AS code, {s}_name AS name FROM items"
        for s in SOURCES
    )
    conn.execute(f"""
        CREATE OR REPLACE TABLE titles AS
        SELECT n.item, arg_min(n.name, a.m2) AS title
        FROM ({named}) n JOIN polygon_areas a USING (source, code, name)
        GROUP BY n.item
    """)
    cols = ", ".join(f"{s}_code AS code_{s}, {s}_name AS name_{s}" for s in SOURCES)
    out = _out("items.json")
    conn.execute(f"""
        COPY (SELECT item, t.title, type, drawn, same_code, missing, s.islands, s.km2,
                [s.xmin, s.ymin, s.xmax, s.ymax] AS bbox,
                (SELECT list(DISTINCT pair ORDER BY pair) FROM patches p
                 WHERE p.item = i.item
                    AND NOT (p.type = 'land' AND p.side = 'both')) AS pairs,
                {cols}
            FROM items i LEFT JOIN stats s USING (item)
            LEFT JOIN titles t USING (item)
            WHERE type <> 'island' OR item IN (SELECT item FROM patches)
            ORDER BY type, s.km2 DESC) TO '{out}' (FORMAT JSON, ARRAY true)
    """)
    n = conn.execute(f"SELECT count(*) FROM read_json('{out}')").fetchall()[0][0]
    _log(f"items.json: {n} items")


# Each phase reads the tables the phases before it left in the database.
PHASES = {"land": _land, "assign": _assign, "overlay": _overlay, "review": _review}
OUTPUTS = [
    OUT / "differences.parquet",
    OUT / "items.json",
    DOTS / "differences_dots.parquet",
]


def inputs() -> list[Path]:
    """Local files the differences derive from, code included."""
    local = [p for p in [*POLYGONS.values(), *LINES] if not isinstance(p, str)]
    code = [Path(__file__), Path(compare_review.__file__)]
    code += [Path(compare.__file__), Path(compare_attributes.__file__)]
    return [*code, OSM_LAND, *VORONOI.values(), *local]


def connect(*, keep: bool) -> duckdb.DuckDBPyConnection:
    """Open the state database, fresh unless ``keep``, spilling to tmp/compare."""
    if not keep:
        DB.unlink(missing_ok=True)
    conn = duckdb.connect(DB)
    conn.execute(f"""
        LOAD spatial; INSTALL httpfs; LOAD httpfs;
        SET threads = {THREADS}; SET memory_limit = '{os.getenv("DIFF_MEMORY", "8GB")}';
        SET temp_directory = '{compare.WORK / "duckdb_tmp"}';
        SET geometry_always_xy = true; SET preserve_insertion_order = false""")
    return conn


def build(start: str = "land", *, force: bool = False) -> bool:
    """Rebuild the differences when stale or from ``start``; return whether it ran."""
    download()
    if not compare.fresh(OSM_LAND, [OSM_DIR / "reefs.json", *compare.files(OSM_DIR)]):
        osm_land(compare.connect())
    names = list(PHASES)
    complete = start == names[0] and not _bbox()
    fresh = all(compare.fresh(o, inputs()) for o in OUTPUTS)
    if complete and not force and fresh and not PARTIAL.exists():
        return False
    # Until a full run succeeds, plain runs rebuild, since resumed state may be stale.
    if not _bbox():
        PARTIAL.touch()
    conn = connect(keep=start != names[0])
    for name in names[names.index(start) :]:
        _log(f"phase {name}")
        PHASES[name](conn)
    conn.close()
    if complete:
        PARTIAL.unlink()
    return True


def main() -> None:
    """Write land and island differences for every source pair."""
    parser = ArgumentParser()
    parser.add_argument("--from", dest="start", choices=PHASES, default="land")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        build(args.start, force=args.force)
    except (duckdb.Error, ValueError, OSError) as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()

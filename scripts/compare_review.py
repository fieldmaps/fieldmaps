"""Group source differences into review items, and border shifts into borders."""

from collections import defaultdict
from hashlib import md5
from math import floor

import duckdb

SOURCES: list[str] = []
# Differing islands with one assignment pattern in neighbouring cells form one item.
GRID = 2


def _id(*parts: object) -> str:
    return md5("|".join(map(str, parts)).encode(), usedforsecurity=False).hexdigest()[
        :12
    ]


def _clusters(conn: duckdb.DuckDBPyConnection) -> None:
    """Join entities that are mutual best matches in any source pair."""
    parent: dict[tuple, tuple] = {}

    def find(x: tuple) -> tuple:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for key in conn.execute("SELECT source, entity FROM entities").fetchall():
        find(key)
    mutual = conn.execute("SELECT a, a_entity, b, b_entity FROM matches WHERE mutual")
    for a, ae, b, be in mutual.fetchall():
        parent[find((a, ae))] = find((b, be))
    # Landless entities never overlap, so a shared code or name joins them instead.
    first: dict[str, tuple] = {}
    for s, e, code, name in conn.execute("""
        SELECT source, entity, upper(code), lower(name) FROM entities
        WHERE (source, entity) NOT IN (SELECT source, entity FROM pieces)
            AND (source, entity) NOT IN (SELECT source, entity FROM placed)
    """).fetchall():
        for key in (f"code:{code}" if code else None, f"name:{name}" if name else None):
            if key and first.setdefault(key, (s, e))[0] != s:
                parent[find((s, e))] = find(first[key])
    ids: dict[tuple, int] = {}
    rows = [(*k, ids.setdefault(find(k), len(ids) + 1)) for k in sorted(parent)]
    conn.execute(
        "CREATE OR REPLACE TABLE clusters "
        "(source VARCHAR, entity VARCHAR, cluster INTEGER)"
    )
    conn.executemany("INSERT INTO clusters VALUES (?, ?, ?)", rows)


def _components(cells: dict[tuple, list]) -> list[tuple[tuple, list]]:
    """Split grid cells into connected groups, each keyed by its lowest cell."""
    seen: set[tuple] = set()
    out = []
    for start in sorted(cells):
        if start in seen:
            continue
        seen.add(start)
        stack, members = [start], []
        while stack:
            cx, cy = stack.pop()
            members += cells[(cx, cy)]
            for nb in ((cx + dx, cy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                if nb in cells and nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        out.append((start, members))
    return out


def _island_items(conn: duckdb.DuckDBPyConnection, label: dict) -> tuple[list, list]:
    """Group each source's islands that another source's cells give another cluster."""
    pivot = ", ".join(
        f"""max(p.entity) FILTER (p.source = '{s}') AS {s},
            max(c.cluster) FILTER (p.source = '{s}') AS {s}_c"""
        for s in SOURCES
    )
    rows = conn.execute(f"""
        SELECT pid, i.source, {", ".join(f"{s}, {s}_c" for s in SOURCES)},
            ST_X(i.pt), ST_Y(i.pt)
        FROM (SELECT pid, {pivot} FROM part_placed p
              LEFT JOIN clusters c USING (source, entity) GROUP BY pid)
        JOIN island_parts i USING (pid)
    """).fetchall()
    groups: dict[tuple, dict] = defaultdict(lambda: defaultdict(list))
    for pid, drawn, *vals, x, y in rows:
        ents, cls = tuple(vals[0::2]), vals[1::2]
        if all(c == cls[SOURCES.index(drawn)] for c in cls):
            continue
        groups[(drawn, ents)][(floor(x / GRID), floor(y / GRID))].append(pid)
    members, entities = [], []
    for (drawn, ents), cells in groups.items():
        for start, pids in _components(cells):
            item = _id(
                "island",
                drawn,
                *(label.get(k) for k in zip(SOURCES, ents, strict=True)),
                start,
            )
            members += [(pid, item, drawn) for pid in pids]
            entities += [
                (item, "island", *k, None) for k in zip(SOURCES, ents, strict=True)
            ]
    return members, entities


def _entity_items(conn: duckdb.DuckDBPyConnection, label: dict) -> list:
    """Clusters missing from a source, with what that source has there instead."""
    clusters: dict[int, list] = defaultdict(list)
    for s, e, cl in conn.execute("SELECT * FROM clusters").fetchall():
        clusters[cl].append((s, e))
    land = set(conn.execute("SELECT DISTINCT source, entity FROM pieces").fetchall())
    placed = set(conn.execute("SELECT DISTINCT source, entity FROM placed").fetchall())
    # A cluster chained across every source still needs items for its unmatched land.
    owners = set(
        conn.execute("""
        SELECT DISTINCT a, a_entity FROM land_diff WHERE side = 'a'
        UNION SELECT DISTINCT b, b_entity FROM land_diff WHERE side = 'b'""").fetchall()
    )
    overlap: dict[tuple, dict] = defaultdict(lambda: defaultdict(float))
    for a, ae, b, be, km2 in conn.execute(
        "SELECT a, a_entity, b, b_entity, km2 FROM weights"
    ).fetchall():
        overlap[(a, ae)][(b, be)] += km2
        overlap[(b, be)][(a, ae)] += km2
    out = []
    for members in clusters.values():
        own = {s for s, _ in members}
        has_land = any(m in land for m in members)
        complete = len(own) == len(SOURCES) and not any(m in owners for m in members)
        if complete or (not has_land and any(m in placed for m in members)):
            continue
        kind = "land" if has_land else "no_land"
        item = _id(kind, *sorted(label.get(m) for m in members))
        out += [(item, kind, *m, True) for m in members]
        for t in set(SOURCES) - own:
            near: dict[tuple, float] = defaultdict(float)
            for m in members:
                for other, km2 in overlap[m].items():
                    if other[0] == t:
                        near[other] += km2
            if near:
                out.append((item, kind, *max(near, key=near.get), False))
    return out


def build(conn: duckdb.DuckDBPyConnection, sources: list[str]) -> None:
    """Build the items table, and land_review mapping land patches to items."""
    SOURCES[:] = sorted(sources)
    _clusters(conn)
    label = {
        (s, e): f"{code or ''}:{name or ''}"
        for s, e, code, name in conn.execute("SELECT * FROM entities").fetchall()
    }
    members, entities = _island_items(conn, label)
    entities += _entity_items(conn, label)
    conn.execute(
        "CREATE OR REPLACE TABLE item_parts (pid BIGINT, item VARCHAR, drawn VARCHAR)"
    )
    if members:
        conn.executemany("INSERT INTO item_parts VALUES (?, ?, ?)", members)
    conn.execute(
        "CREATE OR REPLACE TABLE item_entities (item VARCHAR, type VARCHAR, "
        "source VARCHAR, entity VARCHAR, own BOOLEAN)"
    )
    conn.executemany("INSERT INTO item_entities VALUES (?, ?, ?, ?, ?)", entities)
    pivot = ", ".join(
        f"""string_agg(DISTINCT e.code, '; ') FILTER (ie.source = '{s}') AS {s}_code,
            string_agg(DISTINCT e.name, '; ') FILTER (ie.source = '{s}') AS {s}_name"""
        for s in SOURCES
    )
    conn.execute(f"""
        CREATE OR REPLACE TABLE entity_land AS
        SELECT source, entity, sum(km2) AS km2, min(x0) AS xmin, min(y0) AS ymin,
            max(x1) AS xmax, max(y1) AS ymax
        FROM pieces GROUP BY ALL;
        CREATE OR REPLACE TABLE stats AS
        SELECT item, count(*) AS islands, sum(i.km2) AS km2,
            min(ST_XMin(i.env)) AS xmin, min(ST_YMin(i.env)) AS ymin,
            max(ST_XMax(i.env)) AS xmax, max(ST_YMax(i.env)) AS ymax
        FROM item_parts JOIN island_parts i USING (pid)
        GROUP BY item
        UNION ALL
        SELECT item, 0, max(k.km2), min(k.xmin), min(k.ymin), max(k.xmax), max(k.ymax)
        FROM item_entities JOIN entity_land k USING (source, entity)
        WHERE own AND type = 'land' GROUP BY item
        UNION ALL
        SELECT item, 0, 0, min(ST_XMin(k.env)), min(ST_YMin(k.env)),
            max(ST_XMax(k.env)), max(ST_YMax(k.env))
        FROM item_entities JOIN polygon_parts k USING (source, entity)
        WHERE own AND type = 'no_land' GROUP BY item;
        CREATE OR REPLACE TABLE items AS
        SELECT ie.item, any_value(ie.type) AS type, any_value(d.drawn) AS drawn,
            count(DISTINCT upper(e.code)) = 1 AND count(e.code) = {len(SOURCES)}
                AS same_code,
            list(DISTINCT ie.source ORDER BY ie.source) FILTER (NOT ie.own) AS missing,
            {pivot}
        FROM item_entities ie LEFT JOIN entities e USING (source, entity)
        LEFT JOIN (SELECT DISTINCT item, drawn FROM item_parts) d USING (item)
        GROUP BY ie.item;
    """)
    _borders(conn)


def _borders(conn: duckdb.DuckDBPyConnection) -> None:
    """Map land patches to items, or to a border item per country pair."""
    conn.execute("""
        CREATE OR REPLACE TABLE cluster_names AS
        SELECT cluster, first(concat_ws(' ', e.code, e.name) ORDER BY source) AS label
        FROM clusters JOIN entities e USING (source, entity) GROUP BY cluster;
        CREATE OR REPLACE TABLE land_items AS
        SELECT DISTINCT source, entity, item FROM item_entities
        WHERE own AND type = 'land';
        CREATE OR REPLACE TABLE land_review AS
        SELECT d.*, least(na.label, nb.label) AS lo, greatest(na.label, nb.label) AS hi,
            CASE d.side WHEN 'a' THEN la.item WHEN 'b' THEN lb.item
                ELSE substr(md5(lo || '|' || hi), 1, 12) END AS item
        FROM land_diff d
        JOIN clusters ca ON ca.source = d.a AND ca.entity = d.a_entity
        JOIN cluster_names na ON na.cluster = ca.cluster
        JOIN clusters cb ON cb.source = d.b AND cb.entity = d.b_entity
        JOIN cluster_names nb ON nb.cluster = cb.cluster
        LEFT JOIN land_items la ON la.source = d.a AND la.entity = d.a_entity
        LEFT JOIN land_items lb ON lb.source = d.b AND lb.entity = d.b_entity;
    """)

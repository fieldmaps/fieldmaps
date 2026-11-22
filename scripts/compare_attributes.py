"""Join every comparison source's ADM0 attributes, M49 and UNTERM on ISO3."""

import html
import re
import sys

import compare
import duckdb

FIELDMAPS = (
    "https://data.source.coop/fieldmaps/international/odbl/humanitarian/"
    "adm0-polygons/adm0_polygons.parquet"
)
UNTERM_URL = "https://conferences.unite.un.org/untermapi/api/term/downloadCountries"
M49_URL = "https://unstats.un.org/unsd/methodology/m49/overview/"
REF_DIR = compare.DOWNLOAD / "un"
OUT = compare.CATALOG / "attributes"
REF = compare.WORK / "ref.parquet"
UNTERM_LANGS = ("English", "French", "Spanish", "Russian", "Chinese", "Arabic")
UNTERM_STATUS = {
    0: "Member State",
    1: "Observer State",
    2: "Member of specialized agencies",
}
M49_COLUMNS = (
    "Region Name",
    "Sub-region Name",
    "Intermediate Region Name",
    "Country or Area",
    "M49 Code",
    "ISO-alpha2 Code",
    "ISO-alpha3 Code",
)
# Per source: join code, the name tiles carry (`tile`), then attribute columns.
COLUMNS: dict[str, dict[str, str]] = {
    "fieldmaps": {
        "code": "iso3",
        "tile": "adm0_name",
        "name": "adm0_name1",
        "mapname": "adm0_name",
        "sovereign": "iso3_grp",
        "status": "status_nm",
        "region": "region1_nm",
    },
    "wp": {
        "code": "GENC_3",
        "tile": "Map_Label",
        "name": "WP_Name",
        "mapname": "Map_Label",
        "status": "US_Recog",
    },
    "overture": {"code": "iso3", "tile": "name", "name": "name"},
    "wb": {
        "code": "ISO_A3",
        "tile": "NAM_0",
        "name": "NAM_0",
        "sovereign": "SOV_ISO_A3",
        "status": "WB_STATUS",
        "region": "CONTINENT",
    },
    "gaul": {
        "code": "ISO3_CODE",
        "tile": "GAUL0_NAME",
        "name": "GAUL0_NAME",
        "region": "CONTINENT",
    },
    "gadm": {"code": "iso3", "tile": "COUNTRY", "name": "COUNTRY"},
    "cgaz": {"code": "shapeGroup", "tile": "shapeName", "name": "shapeName"},
    "ne": {
        "code": "ADM0_A3",
        "tile": "NAME",
        "name": "NAME",
        "sovereign": "SOV_A3",
        "status": "TYPE",
        "region": "CONTINENT",
    },
    "unterm": {"code": "iso3", "name": "name_en_short", "status": "un_status"},
    "m49": {"code": "iso3", "name": "name_m49", "region": "region"},
}
POLYGONS = {
    "fieldmaps": FIELDMAPS,
    **{s: compare.output(s, "polygons") for s in compare.SOURCES},
}
# Boxes wider than a hemisphere shift western parts east by 360 when that gives
# the narrower box, so east can pass 180.
BBOX = """CASE WHEN max(x1) - min(x0) <= greatest(180, max(e1) - min(e0))
    THEN [min(x0), min(y0), max(x1), max(y1)]
    ELSE [min(e0), min(y0), max(e1), max(y1)] END"""


def download() -> None:
    """Fetch the UNTERM country list and the M49 overview page."""
    compare.download(UNTERM_URL, REF_DIR / "unterm.xlsx")
    compare.download(M49_URL, REF_DIR / "m49.html")


def _strip_stars(s: str) -> str:
    return re.sub(r"\s*\*+$", "", s)


def _key(name: str) -> str:
    """Match UNTERM names ("Sudan (the)", "Côte d'Ivoire") to M49 names."""
    name = _strip_stars(name.strip())
    name = re.sub(r"\s*\((the|The)\)$", "", name)
    return name.replace("\N{RIGHT SINGLE QUOTATION MARK}", "'").strip().lower()


def _m49_rows() -> list[dict[str, str]]:
    """Rows of the UNSD M49 overview table, keyed by its header names."""
    page = (REF_DIR / "m49.html").read_text(encoding="utf-8")
    start = page.find('id="ENG_Overview"')
    if start < 0:
        msg = "M49 page has no ENG_Overview table"
        raise ValueError(msg)
    table = re.sub(
        r"<!--.*?-->", "", page[start : page.find("</table>", start)], flags=re.DOTALL
    )
    head, *body = [
        [
            html.unescape(re.sub("<[^>]+>", "", td)).strip()
            for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.DOTALL)
        ]
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.DOTALL)
    ]
    if missing := [c for c in M49_COLUMNS if c not in head]:
        msg = f"M49 table lacks columns: {missing}"
        raise ValueError(msg)
    rows = [
        dict(zip(head, cells, strict=True)) for cells in body if len(cells) == len(head)
    ]
    return [r for r in rows if r["M49 Code"].isdigit()]


def ref(conn: duckdb.DuckDBPyConnection) -> None:
    """Join UNTERM names to M49 codes and regions, one row per M49 area."""
    conn.execute("INSTALL excel; LOAD excel")
    unterm = conn.execute(f"""
        SELECT * FROM read_xlsx('{REF_DIR / "unterm.xlsx"}', all_varchar=true)
        WHERE "English short" IS NOT NULL
    """).fetchall()
    cols = [d[0].strip() for d in conn.description]
    by_key = {
        _key(r[cols.index("English short")]): dict(zip(cols, r, strict=True))
        for r in unterm
    }
    out, used = [], set()
    for m in _m49_rows():
        u = by_key.get(_key(m["Country or Area"]))
        if u:
            used.add(_key(m["Country or Area"]))
        short = u["English short"] if u else ""
        stars = len(short.strip()) - len(short.strip().rstrip("*"))
        clean = {k: _strip_stars((v or "").strip()) for k, v in (u or {}).items()}
        out.append(
            {
                "iso3": m["ISO-alpha3 Code"],
                "iso2": m["ISO-alpha2 Code"],
                "m49": m["M49 Code"],
                "name_m49": m["Country or Area"],
                "un_status": UNTERM_STATUS[stars] if u else "Other area",
                **{
                    f"name_{lang[:2].lower()}_{form}": clean.get(f"{lang} {form}", "")
                    for lang in UNTERM_LANGS
                    for form in ("short", "formal")
                },
                "region": m["Region Name"],
                "subregion": m["Sub-region Name"],
                "intermediate_region": m["Intermediate Region Name"],
            }
        )
    if missing := sorted(set(by_key) - used):
        msg = f"UNTERM names with no M49 match: {missing}"
        raise ValueError(msg)
    conn.execute(
        "CREATE TABLE ref (" + ", ".join(f'"{c}" VARCHAR' for c in out[0]) + ")"
    )
    conn.executemany(
        f"INSERT INTO ref VALUES ({', '.join('?' * len(out[0]))})",
        [list(r.values()) for r in out],
    )
    conn.execute(
        f"COPY (SELECT * FROM ref ORDER BY iso3) TO '{REF}' "
        "(FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 15)"
    )


def _parts(conn: duckdb.DuckDBPyConnection) -> None:
    """Load every polygon of every source's features into ``parts``."""
    features = " UNION ALL ".join(
        f"""SELECT upper({c["code"]}) AS iso3, '{s}' AS source,
            '{s}' AS layer, {rank} AS rank, row_number() OVER () AS fid,
            {c["tile"]} AS name,
            coalesce(nullif(trim({c["tile"]}::VARCHAR), ''), {c["name"]}) AS label,
            geometry
        FROM read_parquet('{POLYGONS[s]}')"""
        for rank, (s, c) in enumerate((s, COLUMNS[s]) for s in POLYGONS)
    )
    conn.execute(f"""
        CREATE TABLE parts AS
        SELECT *, CASE WHEN x1 <= 0 THEN x0 + 360 ELSE x0 END AS e0,
               CASE WHEN x1 <= 0 THEN x1 + 360 ELSE x1 END AS e1
        FROM (SELECT iso3, source, layer, rank, fid, trim(name::VARCHAR) AS name,
                trim(label::VARCHAR) AS label, ST_Area(part) AS area,
                round(ST_XMin(part), 3) AS x0, round(ST_XMax(part), 3) AS x1,
                round(ST_YMin(part), 3) AS y0, round(ST_YMax(part), 3) AS y1
            FROM (SELECT * EXCLUDE geometry, unnest(ST_Dump(geometry)).geom AS part
                FROM ({features}) WHERE iso3 IS NOT NULL))
    """)
    conn.execute(f"""
        CREATE TABLE features AS
        SELECT iso3, source, layer, fid, source || ':' || fid AS id,
               any_value(rank) AS rank, any_value(name) AS name,
               any_value(label) AS label, sum(area) AS area, {BBOX} AS bbox
        FROM parts GROUP BY 1, 2, 3, 4
    """)


def attributes(conn: duckdb.DuckDBPyConnection) -> None:
    """Write one row per ISO3 code with each source's values side by side."""
    selects = []
    for source, cols in COLUMNS.items():
        table = POLYGONS.get(source, REF)
        aggs = ", ".join(
            f"string_agg(DISTINCT trim({expr}::VARCHAR), ' | ' ORDER BY "
            f"trim({expr}::VARCHAR)) AS {col}_{source}"
            for col, expr in cols.items()
            if col not in {"code", "tile"}
        )
        count = f"count(*) AS count_{source}," if source in POLYGONS else ""
        selects.append(
            f"""(SELECT upper({cols["code"]}) AS iso3, {count} {aggs}
            FROM read_parquet('{table}')
            WHERE {cols["code"]} IS NOT NULL GROUP BY 1) AS {source}"""
        )
    _parts(conn)
    selects.append(f"(SELECT iso3, {BBOX} AS bbox FROM parts GROUP BY 1) AS extent")
    selects.append(
        """(SELECT iso3, list(
                {s: source, id: id, layer: layer, name: name, label: label, bbox: bbox}
                ORDER BY rank, area DESC) AS parts
        FROM features GROUP BY 1) AS features"""
    )
    query = "SELECT * FROM " + " FULL JOIN ".join(
        [selects[0], *(f"{s} USING (iso3)" for s in selects[1:])]
    )
    OUT.mkdir(parents=True, exist_ok=True)
    json = OUT / "attributes.json"
    conn.execute(f"COPY ({query} ORDER BY iso3) TO '{json}' (FORMAT JSON, ARRAY true)")
    conn.execute(
        f"COPY (FROM read_json('{json}')) TO '{OUT / 'attributes.parquet'}' "
        "(FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 15)"
    )
    n, unique = conn.execute(
        f"SELECT count(*), count(DISTINCT iso3) FROM read_json('{json}')"
    ).fetchall()[0]
    if n != unique:
        msg = f"attributes.json: {n} rows but {unique} codes"
        raise ValueError(msg)
    print(f"{json.relative_to(compare.ROOT)}: {n} rows")  # noqa: T201


def build(*, force: bool = False) -> bool:
    """Rebuild ref.parquet and attributes when stale; return whether they changed."""
    downloads = [REF_DIR / "unterm.xlsx", REF_DIR / "m49.html"]
    if not all(p.exists() for p in downloads):
        download()
    local = [p for p in POLYGONS.values() if not isinstance(p, str)]
    out = OUT / "attributes.parquet"
    if not force and compare.fresh(out, [*downloads, *local]):
        return False
    conn = compare.connect()
    if force or not compare.fresh(REF, downloads):
        ref(conn)
    attributes(conn)
    return True


def main() -> None:
    """Download the references, then rebuild the attributes table."""
    download()
    try:
        build(force="--force" in sys.argv)
    except (duckdb.Error, ValueError) as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()

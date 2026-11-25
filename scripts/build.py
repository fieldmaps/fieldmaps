"""Build the site catalog: sources, PMTiles, portolan add, check, push."""

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

import compare
import compare_attributes
import duckdb
import explore_steps
import fieldmaps_publish
import international_steps
import subnational_steps
import tylertoo

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
TMP = ROOT / "tmp" / "catalog"
MAX_ZOOM = {"international": 6, "subnational": 12, "compare": 12, "explore": 12}
STEPS = {
    "international": international_steps.build,
    "subnational": subnational_steps.build,
    "explore": explore_steps.build,
}


EXTRA = {
    "points": {"point_thinning": 0},
    "outlines": {"coalesce_lines": False},
}


def tables(now: str) -> list[str]:
    """Rebuild the attributes when stale; return what failed."""
    try:
        if compare_attributes.build():
            fieldmaps_publish.add(
                CATALOG, "compare/attributes", "--datetime", now, "--force"
            )
    except (duckdb.Error, ValueError, OSError) as e:
        print(f"failed: attributes: {e}")  # noqa: T201
        return [f"attributes: {e}"]
    return []


def main() -> None:
    """Rebuild every collection, validate the catalog, and push it with --push."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--only", choices=MAX_ZOOM)
    args = parser.parse_args()
    now = datetime.now(UTC).replace(microsecond=0).isoformat()
    TMP.mkdir(parents=True, exist_ok=True)
    failed = []
    for story, zoom in MAX_ZOOM.items():
        if args.only and story != args.only:
            continue
        if story == "compare":
            if failed := compare.build():
                print("\n".join(failed))  # noqa: T201
            failed += tables(now)
        else:
            STEPS[story]()
        for parquet in sorted(CATALOG.glob(f"{story}/*/*.parquet")):
            if parquet.parent == compare_attributes.OUT:
                continue
            pmtiles = parquet.with_suffix(".pmtiles")
            if compare.fresh(pmtiles, [parquet]):
                continue
            overview = TMP / f"{story}_{parquet.name}"
            try:
                tylertoo.overview(
                    str(parquet),
                    str(overview),
                    max_zoom=zoom,
                    density_drop=False,
                    line_thinning=0,
                    line_visibility=0,
                    polygon_thinning=0,
                    polygon_visibility=0,
                    **EXTRA.get(parquet.stem, {}),
                )
                tylertoo.export_pmtiles(
                    str(overview),
                    str(pmtiles),
                    layer_name=parquet.stem,
                    tile_size_limit=None,
                )
            finally:
                overview.unlink(missing_ok=True)
            collection = str(parquet.parent.relative_to(CATALOG))
            fieldmaps_publish.add(CATALOG, collection, "--datetime", now, "--force")
            print(collection)  # noqa: T201
    fieldmaps_publish.run(CATALOG, "check", "--data-scope", "local")
    if args.push and failed:
        sys.exit("Not pushing: a compare stage failed.")
    if args.push:
        fieldmaps_publish.push(CATALOG)


if __name__ == "__main__":
    main()

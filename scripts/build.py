"""Build the site demo catalog: step SQL, PMTiles, portolan add, check, push."""

import argparse
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import fieldmaps_publish
import tylertoo

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
TMP = ROOT / "tmp" / "catalog"
MAX_ZOOM = {"international": 6, "subnational": 12}
ENV = {
    "international": {"FIELDMAPS_BUILD": "../international"},
    "subnational": {"FIELDMAPS": "..", "TZA_DEBUG": "tmp/tza-debug/work"},
}


def main() -> None:
    """Rebuild every collection, validate the catalog, and push it with --push."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()
    now = datetime.now(UTC).replace(microsecond=0).isoformat()
    TMP.mkdir(parents=True, exist_ok=True)
    for story, zoom in MAX_ZOOM.items():
        subprocess.run(
            ["duckdb", "-no-agent", "-c", f".read scripts/{story}-steps.sql"],
            cwd=ROOT,
            env={**os.environ, **ENV[story]},
            check=True,
        )
        for parquet in sorted(CATALOG.glob(f"{story}/*/*.parquet")):
            overview = TMP / f"{story}_{parquet.name}"
            tylertoo.overview(
                str(parquet),
                str(overview),
                max_zoom=zoom,
                density_drop=False,
                line_thinning=0,
                line_visibility=0,
                polygon_thinning=0,
                polygon_visibility=0,
            )
            tylertoo.export_pmtiles(
                str(overview),
                str(parquet.with_suffix(".pmtiles")),
                layer_name=parquet.stem,
                tile_size_limit=None,
            )
            overview.unlink()
            collection = str(parquet.parent.relative_to(CATALOG))
            fieldmaps_publish.add(CATALOG, collection, "--datetime", now, "--force")
            print(collection)  # noqa: T201
    fieldmaps_publish.run(CATALOG, "check", "--data-scope", "local")
    if args.push:
        fieldmaps_publish.push(CATALOG)


if __name__ == "__main__":
    main()

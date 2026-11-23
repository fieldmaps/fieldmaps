# Boundary comparison island dots

One point per island difference, at the island's maximum inscribed circle centre, so small differing islands stay visible on the comparison map. Islands within five of their own widths of a larger island in the same item get no dot. Built by `scripts/compare_differences.py`.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/differences-dots/differences_dots.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/differences-dots/differences_dots.pmtiles`, layer `differences_dots`, every point kept at every zoom
- Columns: `pair`, `side`, `item` as in the `differences` collection, and `geometry`.

## License

ODbL 1.0, as a derivative of OpenStreetMap land polygons. Attribution: © OpenStreetMap contributors, and each compared source.

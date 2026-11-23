# Boundary comparison differences

Where each pair of the eight comparison sources disagrees about land. Built by `scripts/compare_differences.py` on OpenStreetMap land polygons; the page's Geometry tab reads `items.json` and draws the PMTiles in Voronoi mode.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/differences/differences.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/differences/differences.pmtiles`, layer `differences`
- JSON: `https://data.source.coop/fieldmaps/site/compare/differences/items.json`, one entry per review item
- `pair`: two source ids sorted and joined with `|`, e.g. `fieldmaps|wp`. Sources: `cgaz`, `fieldmaps`, `gadm`, `gaul`, `ne`, `overture`, `wb`, `wp`.
- `type`: `land` (OSM land the two sources put in territories that are not each other's best match), `island` (an island one source draws, in a zone where the other's Voronoi puts it in a different territory), `voronoi` (the Voronoi area around a difference, for picking).
- `side`: `a` or `b` for the source in `pair` order the patch belongs to, `both` for border shifts between matched territories.
- `item`: the review item in `items.json`; `a_code`, `a_name`, `b_code`, `b_name`: each side's territory; `km2`: area.
- `items.json` fields: `item`, `title`, `type` (`land`, `island`, `no_land`), `drawn` (source drawing an island item), `missing` (sources with no territory of their own there), `islands`, `km2`, `bbox`, `pairs`, and `code_{source}`, `name_{source}` per source.

```sql
LOAD spatial;
SELECT pair, type, a_name, b_name, round(km2, 1) AS km2
FROM 'https://data.source.coop/fieldmaps/site/compare/differences/differences.parquet'
WHERE type = 'land' AND side <> 'both' ORDER BY km2 DESC LIMIT 20;
```

## License

ODbL 1.0, as a derivative of OpenStreetMap land polygons. Attribution: © OpenStreetMap contributors, and each compared source; see the source collections' READMEs.

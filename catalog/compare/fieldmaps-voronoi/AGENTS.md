# FieldMaps Voronoi

Polygons extended over water from FieldMaps international boundaries (humanitarian, OSM land). Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/fieldmaps-voronoi/fieldmaps_voronoi.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/fieldmaps-voronoi/fieldmaps_voronoi.pmtiles`, layer `fieldmaps_voronoi`
- Columns: the attributes of `international/odbl/humanitarian/adm0-polygons` (release 2026-11-20), joined on the `adm0_id` code without its date suffix, plus `geometry`. Country code: `iso3`. Name: `adm0_name`
- 323 polygons, the 2026-10-31 FieldMaps polygons extended over water and gaps (topo-tools edge-extend) to cover the whole globe

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/fieldmaps-voronoi/fieldmaps_voronoi.parquet' LIMIT 10;
```

## License

Open Database License (ODbL) 1.0. Attribution: © OpenStreetMap contributors, U.S. Department of State, FieldMaps.

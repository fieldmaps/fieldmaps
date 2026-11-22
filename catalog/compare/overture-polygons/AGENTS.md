# Overture Maps Divisions

Overture Maps Foundation divisions theme, release 2026-11-18.0, country land areas. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/overture-polygons/overture_polygons.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/overture-polygons/overture_polygons.pmtiles`, layer `overture_polygons`
- Columns: every source attribute as published, plus `geometry`. Country code: `iso3` (ISO3, added from the Overture `country` code via M49, with TW as TWN and XK as XKX, null for 20 of 219 rows). Name: `name`
- 219 polygons forming a clean coverage (no gaps or overlaps up to 1e-8 degrees), with coordinates rounded to 1e-9 degrees

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/overture-polygons/overture_polygons.parquet' LIMIT 10;
```

## License

Open Database License (ODbL) 1.0. Attribution: © OpenStreetMap contributors, Overture Maps Foundation.

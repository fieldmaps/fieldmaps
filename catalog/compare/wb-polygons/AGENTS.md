# World Bank Official Boundaries

World Bank Official Boundaries, Admin 0 (dataset 0038272). Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/wb-polygons/wb_polygons.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/wb-polygons/wb_polygons.pmtiles`, layer `wb_polygons`
- Columns: every source attribute as published, plus `geometry`. Country code: `ISO_A3` (ISO 3166-1 alpha-3, with World Bank codes for some territories, null for 20 of 275 rows). Name: `NAM_0`
- 275 polygons forming a clean coverage (no gaps or overlaps up to 1e-8 degrees), with coordinates rounded to 1e-9 degrees

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/wb-polygons/wb_polygons.parquet' LIMIT 10;
```

## License

Creative Commons Attribution 4.0 (CC BY 4.0). Attribution: World Bank.

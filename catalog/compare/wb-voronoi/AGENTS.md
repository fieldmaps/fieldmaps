# World Bank Official Boundaries Voronoi

Polygons extended over water from World Bank Official Boundaries, Admin 0 (dataset 0038272). Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/wb-voronoi/wb_voronoi.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/wb-voronoi/wb_voronoi.pmtiles`, layer `wb_voronoi`
- Columns: every source attribute as published, plus `geometry`. Country code: `ISO_A3` (ISO 3166-1 alpha-3, with World Bank codes for some territories, null for 20 of 275 rows). Name: `NAM_0`
- 275 polygons, the cleaned polygons extended over water and gaps (topo-tools edge-extend) to cover the whole globe

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/wb-voronoi/wb_voronoi.parquet' LIMIT 10;
```

## License

Creative Commons Attribution 4.0 (CC BY 4.0). Attribution: World Bank.

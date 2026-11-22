# FAO GAUL 2025 Voronoi

Polygons extended over water from FAO Global Administrative Unit Layers 2025, level 1 dissolved to level 0. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/gaul-voronoi/gaul_voronoi.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/gaul-voronoi/gaul_voronoi.pmtiles`, layer `gaul_voronoi`
- Columns: the level 0 attributes of GAUL level 1 (`ISO3_CODE`, `MAP_CODE`, `GAUL0_CODE`, `GAUL0_NAME`, `CONTINENT`), dissolved on them, plus `geometry`. Country code: `ISO3_CODE` (ISO 3166-1 alpha-3). Name: `GAUL0_NAME`
- 272 polygons, the cleaned polygons extended over water and gaps (topo-tools edge-extend) to cover the whole globe

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/gaul-voronoi/gaul_voronoi.parquet' LIMIT 10;
```

## License

Creative Commons Attribution 4.0 (CC BY 4.0), with the GAUL 2025 Terms of Use. Attribution: FAO GAUL 2025.

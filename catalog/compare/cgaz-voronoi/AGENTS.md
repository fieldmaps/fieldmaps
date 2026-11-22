# geoBoundaries CGAZ Voronoi

Polygons extended over water from geoBoundaries Comprehensive Global Administrative Zones (CGAZ), ADM0. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/cgaz-voronoi/cgaz_voronoi.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/cgaz-voronoi/cgaz_voronoi.pmtiles`, layer `cgaz_voronoi`
- Columns: every source attribute as published, plus `geometry`. Country code: `shapeGroup` (ISO 3166-1 alpha-3). Name: `shapeName`
- 218 polygons, the cleaned polygons extended over water and gaps (topo-tools edge-extend) to cover the whole globe

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/cgaz-voronoi/cgaz_voronoi.parquet' LIMIT 10;
```

## License

Creative Commons Attribution 4.0 (CC BY 4.0). Attribution: geoBoundaries.

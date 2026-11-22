# Natural Earth Voronoi

Polygons extended over water from Natural Earth 1:10m Admin 0 Countries. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/ne-voronoi/ne_voronoi.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/ne-voronoi/ne_voronoi.pmtiles`, layer `ne_voronoi`
- Columns: every source attribute as published, plus `OGC_FID_orig` (BIGINT, the source feature id) and `geometry`. Country code: `ADM0_A3` (Natural Earth's three-letter code). Name: `NAME`
- 258 polygons, the cleaned polygons extended over water and gaps (topo-tools edge-extend) to cover the whole globe

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/ne-voronoi/ne_voronoi.parquet' LIMIT 10;
```

## License

Public domain. Attribution: Natural Earth.

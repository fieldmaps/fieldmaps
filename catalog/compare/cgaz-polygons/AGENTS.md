# geoBoundaries CGAZ

geoBoundaries Comprehensive Global Administrative Zones (CGAZ), ADM0. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/cgaz-polygons/cgaz_polygons.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/cgaz-polygons/cgaz_polygons.pmtiles`, layer `cgaz_polygons`
- Columns: every source attribute as published, plus `fid_orig` (BIGINT, the source feature id) and `geometry`. Country code: `shapeGroup` (ISO 3166-1 alpha-3, with numeric codes such as `111` for disputed areas). Name: `shapeName`
- 218 polygons forming a clean coverage (no gaps or overlaps up to 1e-8 degrees), with coordinates rounded to 1e-9 degrees

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/cgaz-polygons/cgaz_polygons.parquet' LIMIT 10;
```

## License

Creative Commons Attribution 4.0 (CC BY 4.0). Attribution: geoBoundaries.

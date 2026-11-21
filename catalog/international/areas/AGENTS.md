# Polygonized areas

Lines polygonized into ADM0 areas, before clipping to land. Shown in the International story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/international/areas/areas.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/international/areas/areas.pmtiles`, layer `areas`
- Columns: `id` (VARCHAR), `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/international/areas/areas.parquet' LIMIT 10;
```

## License

ODbL-1.0. Attribution: © OpenStreetMap contributors, U.S. Department of State, FieldMaps.

# LSIB lines

U.S. Department of State Large Scale International Boundaries lines, merged into continuous lines. Shown in the International story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/international/lsib/lsib.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/international/lsib/lsib.pmtiles`, layer `lsib`
- Columns: `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/international/lsib/lsib.parquet' LIMIT 10;
```

## License

ODbL-1.0. Attribution: © OpenStreetMap contributors, U.S. Department of State, FieldMaps.

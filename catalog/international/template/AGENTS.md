# Extension lines

Manual line edits that extend LSIB around coastal islands and inlets. Shown in the International story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/international/template/template.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/international/template/template.pmtiles`, layer `template`
- Columns: `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/international/template/template.parquet' LIMIT 10;
```

## License

ODbL-1.0. Attribution: © OpenStreetMap contributors, U.S. Department of State, FieldMaps.

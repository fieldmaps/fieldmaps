# Original input

Tanzania ADM3 polygons as published. Shown in the Subnational story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/subnational/original/original.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/subnational/original/original.pmtiles`, layer `original`
- Columns: `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/subnational/original/original.parquet' LIMIT 10;
```

## License

CC-BY-3.0-IGO. Attribution: Tanzania National Bureau of Statistics, UN OCHA ROSA, FieldMaps.

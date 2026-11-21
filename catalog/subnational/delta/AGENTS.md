# Original input (Rufiji delta)

Original polygons clipped to a small area of the Rufiji delta. Shown in the Subnational story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/subnational/delta/delta.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/subnational/delta/delta.pmtiles`, layer `delta`
- Columns: `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/subnational/delta/delta.parquet' LIMIT 10;
```

## License

CC-BY-3.0-IGO. Attribution: Tanzania National Bureau of Statistics, UN OCHA ROSA, FieldMaps.

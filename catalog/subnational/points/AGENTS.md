# Outline points (Rufiji delta)

Points from outline vertices and segment breaks in the Rufiji delta. Shown in the Subnational story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/subnational/points/points.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/subnational/points/points.pmtiles`, layer `points`
- Columns: `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/subnational/points/points.parquet' LIMIT 10;
```

## License

CC-BY-3.0-IGO. Attribution: Tanzania National Bureau of Statistics, UN OCHA ROSA, FieldMaps.

# ISO3 points

Companion points giving the ISO3 code for each area enclosed by the lines. Shown in the International story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/international/points/points.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/international/points/points.pmtiles`, layer `points`
- Columns: `id` (VARCHAR), `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/international/points/points.parquet' LIMIT 10;
```

## License

ODbL-1.0. Attribution: © OpenStreetMap contributors, U.S. Department of State, FieldMaps.

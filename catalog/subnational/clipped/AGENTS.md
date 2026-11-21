# Clipped to ADM0

Extended polygons clipped to the FieldMaps ADM0 boundary. Shown in the Subnational story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/subnational/clipped/clipped.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/subnational/clipped/clipped.pmtiles`, layer `clipped`
- Columns: `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/subnational/clipped/clipped.parquet' LIMIT 10;
```

## License

ODbL-1.0. Attribution: © OpenStreetMap contributors, U.S. Department of State, FieldMaps.

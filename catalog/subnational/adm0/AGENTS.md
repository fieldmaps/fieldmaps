# ADM0 boundary

FieldMaps ADM0 polygons for each country, from the OpenStreetMap-based humanitarian view. Shown in the Subnational story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/subnational/adm0/adm0.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/subnational/adm0/adm0.pmtiles`, layer `adm0`
- Columns: `iso3` (VARCHAR), `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/subnational/adm0/adm0.parquet' WHERE iso3 = 'NIC' LIMIT 10;
```

## License

ODbL-1.0. Attribution: © OpenStreetMap contributors, U.S. Department of State, FieldMaps.

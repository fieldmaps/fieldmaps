# Mismatch with ADM0

Where each country's dissolved original polygons differ from its FieldMaps ADM0 polygon. Shown in the Subnational story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/subnational/mismatch/mismatch.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/subnational/mismatch/mismatch.pmtiles`, layer `mismatch`
- Columns: `iso3` (VARCHAR), `kind` (VARCHAR: `gap` is ADM0 area the source leaves out, `spill` is source area beyond ADM0), `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/subnational/mismatch/mismatch.parquet' WHERE iso3 = 'NIC' LIMIT 10;
```

## License

ODbL-1.0. Attribution: © OpenStreetMap contributors, U.S. Department of State, GADM, OCHA FISS, Tanzania NBS, OCHA ROSA, IEBC, OCHA ROSEA, FieldMaps.

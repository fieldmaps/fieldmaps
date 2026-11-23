# Outline points

Points placed along the outlines, each keeping its polygon. Shown in the Subnational story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/subnational/points/points.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/subnational/points/points.pmtiles`, layer `points`
- Columns: `iso3` (VARCHAR), `fid` (BIGINT, the source polygon), `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/subnational/points/points.parquet' WHERE iso3 = 'NIC' LIMIT 10;
```

## License

CC-BY-3.0-IGO. Attribution: GADM, OCHA FISS, Tanzania NBS, OCHA ROSA, IEBC, OCHA ROSEA, FieldMaps.

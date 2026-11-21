# Polygon outlines

Outer edges of the original polygons, keeping the attributes of the polygon each segment came from. Shown in the Subnational story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/subnational/outlines/outlines.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/subnational/outlines/outlines.pmtiles`, layer `outlines`
- Columns: `fid` (BIGINT), `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/subnational/outlines/outlines.parquet' LIMIT 10;
```

## License

CC-BY-3.0-IGO. Attribution: Tanzania National Bureau of Statistics, UN OCHA ROSA, FieldMaps.

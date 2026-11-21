# Extended polygons

Original polygons merged with the dissolved Voronoi cells, extending them outward. Shown in the Subnational story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/subnational/extended/extended.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/subnational/extended/extended.pmtiles`, layer `extended`
- Columns: `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/subnational/extended/extended.parquet' LIMIT 10;
```

## License

CC-BY-3.0-IGO. Attribution: Tanzania National Bureau of Statistics, UN OCHA ROSA, FieldMaps.

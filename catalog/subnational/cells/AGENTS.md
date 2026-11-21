# Voronoi cells (Rufiji delta)

Voronoi polygons from the outline points in the Rufiji delta, each carrying its source polygon's attributes. Shown in the Subnational story on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/subnational/cells/cells.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/subnational/cells/cells.pmtiles`, layer `cells`
- Columns: `fid` (BIGINT), `geom` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/subnational/cells/cells.parquet' LIMIT 10;
```

## License

CC-BY-3.0-IGO. Attribution: Tanzania National Bureau of Statistics, UN OCHA ROSA, FieldMaps.

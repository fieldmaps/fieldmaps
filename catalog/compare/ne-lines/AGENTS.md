# Natural Earth lines

International boundary lines from Natural Earth 1:10m Admin 0 Countries. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/ne-lines/ne_lines.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/ne-lines/ne_lines.pmtiles`, layer `ne_lines`
- Columns: `a_code`, `a_name`, `b_code`, `b_name` (the country code and name on each side, from the polygons), `line_type` (`international`) and `geometry`
- 393 lines, the shared edges of the cleaned polygons

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/ne-lines/ne_lines.parquet' LIMIT 10;
```

## License

Public domain. Attribution: Natural Earth.

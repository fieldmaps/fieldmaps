# US State Department lines

International boundary lines from U.S. Department of State Large Scale International Boundaries (LSIB). Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/wp-lines/wp_lines.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/wp-lines/wp_lines.pmtiles`, layer `wp_lines`
- Columns: every LSIB attribute as published, plus `line_type` from `STATUS` (`international`, `armistice` for other lines of international separation, `special`)
- 395 lines

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/wp-lines/wp_lines.parquet' LIMIT 10;
```

## License

Terms set by the publisher at https://geodata.state.gov. Attribution: U.S. Department of State.

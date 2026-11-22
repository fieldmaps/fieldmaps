# World Bank Official Boundaries lines

International boundary lines from World Bank Official Boundaries, Admin 0 (dataset 0038272). Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/wb-lines/wb_lines.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/wb-lines/wb_lines.pmtiles`, layer `wb_lines`
- Columns: `a_code`, `a_name`, `b_code`, `b_name` (the country code and name on each side, from the polygons, so a code is null where the polygon's code is null), `line_type` (`international`) and `geometry`
- 649 lines, the shared edges of the cleaned polygons

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/wb-lines/wb_lines.parquet' LIMIT 10;
```

## License

Creative Commons Attribution 4.0 (CC BY 4.0). Attribution: World Bank.

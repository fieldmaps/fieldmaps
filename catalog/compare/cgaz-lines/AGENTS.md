# geoBoundaries CGAZ lines

International boundary lines from geoBoundaries Comprehensive Global Administrative Zones (CGAZ), ADM0. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/cgaz-lines/cgaz_lines.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/cgaz-lines/cgaz_lines.pmtiles`, layer `cgaz_lines`
- Columns: `a_code`, `a_name`, `b_code`, `b_name` (the country code and name on each side, from the polygons), `line_type` (`international`) and `geometry`
- 622 lines, the shared edges of the cleaned polygons

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/cgaz-lines/cgaz_lines.parquet' LIMIT 10;
```

## License

Creative Commons Attribution 4.0 (CC BY 4.0). Attribution: geoBoundaries.

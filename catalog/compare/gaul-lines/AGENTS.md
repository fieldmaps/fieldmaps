# FAO GAUL 2025 lines

International boundary lines from FAO Global Administrative Unit Layers 2025, level 1 dissolved to level 0. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/gaul-lines/gaul_lines.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/gaul-lines/gaul_lines.pmtiles`, layer `gaul_lines`
- Columns: `a_code`, `a_name`, `b_code`, `b_name` (the country code and name on each side, from the polygons), `line_type` (`international`) and `geometry`
- 428 lines, the shared edges of the cleaned polygons

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/gaul-lines/gaul_lines.parquet' LIMIT 10;
```

## License

Creative Commons Attribution 4.0 (CC BY 4.0), with the GAUL 2025 Terms of Use. Attribution: FAO GAUL 2025.

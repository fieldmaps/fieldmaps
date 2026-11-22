# GADM 4.1 lines

International boundary lines from GADM 4.1, level 0, without the Caspian Sea. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/gadm-lines/gadm_lines.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/gadm-lines/gadm_lines.pmtiles`, layer `gadm_lines`
- Columns: `a_code`, `a_name`, `b_code`, `b_name` (the country code and name on each side, from the polygons), `line_type` (`international`) and `geometry`
- 1647 lines, the shared edges of the cleaned polygons

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/gadm-lines/gadm_lines.parquet' LIMIT 10;
```

## License

Free for academic and other non-commercial use. Redistribution or commercial use is not allowed without prior permission from GADM. Attribution: GADM.

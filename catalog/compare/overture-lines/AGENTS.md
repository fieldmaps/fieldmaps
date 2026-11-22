# Overture Maps Divisions lines

International boundary lines from Overture Maps Foundation divisions theme, release 2026-11-18.0, country land areas. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/overture-lines/overture_lines.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/overture-lines/overture_lines.pmtiles`, layer `overture_lines`
- Columns: every `division_boundary` attribute as published, for country land boundaries, plus `line_type` (`armistice` where `is_disputed`, else `international`)
- 374 lines

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/overture-lines/overture_lines.parquet' LIMIT 10;
```

## License

Open Database License (ODbL) 1.0. Attribution: © OpenStreetMap contributors, Overture Maps Foundation.

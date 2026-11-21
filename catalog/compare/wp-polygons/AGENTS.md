# US State Department World Polygons

U.S. Department of State World Polygons, full-resolution layer. Shown on the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/wp-polygons/wp_polygons.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/wp-polygons/wp_polygons.pmtiles`, layer `wp_polygons`
- Columns: every World Polygons attribute as published (all VARCHAR), plus `fid_orig` (BIGINT, the source feature id) and `geometry` (geometry, `OGC:CRS84`). Country code: `GENC_3` (GENC three-letter code, null for 2 of 323 rows). Name: `WP_Name`. Other attributes: `WP_Name_ND`, `DOS_Short`, `DOS_Long`, `Map_Label`, `US_Recog`, `Show_Disp`, `Map_Disp`, `NOTES`, `NOTES_Cont`, `MapTint_2`, `MapTint_3`, `GENC_Short`, `GENC_Full`, `GENC_2`, `ISO_3166_1`, `ISO_3166_2`, `WP_ID`, `WP_PREV_ID`, `WP_PAR_ID`
- Polygons form a clean coverage (no gaps or overlaps up to 1e-8 degrees), with coordinates rounded to 1e-9 degrees

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/wp-polygons/wp_polygons.parquet' LIMIT 10;
```

## License

Terms set by the publisher at https://geodata.state.gov. Attribution: U.S. Department of State.

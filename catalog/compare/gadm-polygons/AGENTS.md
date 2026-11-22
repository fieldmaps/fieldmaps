# GADM 4.1

GADM 4.1, level 0, without the Caspian Sea. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/gadm-polygons/gadm_polygons.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/gadm-polygons/gadm_polygons.pmtiles`, layer `gadm_polygons`
- Columns: every source attribute as published, plus `geometry`. Country code: `iso3` (`GID_0` with Kosovo as XKX). Name: `COUNTRY`
- 262 polygons forming a clean coverage (no gaps or overlaps up to 1e-8 degrees), with coordinates rounded to 1e-9 degrees

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/gadm-polygons/gadm_polygons.parquet' LIMIT 10;
```

## License

Free for academic and other non-commercial use. Redistribution or commercial use is not allowed without prior permission from GADM. Attribution: GADM.

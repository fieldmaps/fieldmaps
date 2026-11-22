# GADM 4.1 Voronoi

Polygons extended over water from GADM 4.1, level 0, without the Caspian Sea. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/gadm-voronoi/gadm_voronoi.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/gadm-voronoi/gadm_voronoi.pmtiles`, layer `gadm_voronoi`
- Columns: every source attribute as published, plus `fid_orig` (BIGINT, the source feature id) and `geometry`. Country code: `iso3` (`GID_0` with Kosovo as XKX). Name: `COUNTRY`
- 262 polygons, the cleaned polygons extended over water and gaps (topo-tools edge-extend) to cover the whole globe

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/gadm-voronoi/gadm_voronoi.parquet' LIMIT 10;
```

## License

Free for academic and other non-commercial use. Redistribution or commercial use is not allowed without prior permission from GADM. Attribution: GADM.

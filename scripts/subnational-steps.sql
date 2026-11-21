-- Writes catalog/subnational/*/*.parquet from fieldmaps/subnational and fieldmaps/international catalogs and a Tanzania edge-extend --debug run.
-- FIELDMAPS=.. TZA_DEBUG=tmp/tza-debug/work duckdb -c ".read scripts/subnational-steps.sql"
LOAD spatial;
SET geometry_always_xy = true;
SET threads = 5;
SET VARIABLE root = getenv('FIELDMAPS');
SET VARIABLE debug = getenv('TZA_DEBUG');
SET VARIABLE delta = ST_MakeEnvelope(39.2, -7.95, 39.35, -7.8);

CREATE MACRO crs(g) AS ST_SetCRS(g, 'OGC:CRS84');
CREATE MACRO delta(g) AS crs(ST_Intersection(g, getvariable('delta')));

COPY (SELECT crs(geometry) AS geom FROM read_parquet(getvariable('root') || '/subnational/catalog/source/tza/tza_original.parquet'))
  TO 'catalog/subnational/original/original.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT fid, crs(ST_LineMerge(geom)) AS geom FROM read_parquet(getvariable('debug') || '/tza_original_parquet_02.parquet'))
  TO 'catalog/subnational/outlines/outlines.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT delta(geometry) AS geom FROM read_parquet(getvariable('root') || '/subnational/catalog/source/tza/tza_original.parquet')
  WHERE ST_Intersects(geometry, getvariable('delta')))
  TO 'catalog/subnational/delta/delta.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT crs(geom) AS geom FROM read_parquet(getvariable('debug') || '/tza_original_parquet_03b.parquet')
  WHERE ST_Intersects(geom, getvariable('delta')))
  TO 'catalog/subnational/points/points.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT fid, delta(geom) AS geom FROM read_parquet(getvariable('debug') || '/tza_original_parquet_04_tmp2.parquet')
  WHERE ST_Intersects(geom, getvariable('delta')))
  TO 'catalog/subnational/cells/cells.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT crs(geometry) AS geom FROM read_parquet(getvariable('root') || '/subnational/catalog/source/tza/tza_extended.parquet'))
  TO 'catalog/subnational/extended/extended.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT crs(geometry) AS geom FROM read_parquet(getvariable('root') || '/subnational/catalog/iso3/tza/adm3_polygons.parquet'))
  TO 'catalog/subnational/clipped/clipped.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT crs(geometry) AS geom FROM read_parquet(getvariable('root') || '/international/catalog/odbl/humanitarian/adm0-polygons/adm0_polygons.parquet')
  WHERE iso3 = 'TZA')
  TO 'catalog/subnational/adm0/adm0.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);

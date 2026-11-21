-- Writes catalog/subnational/*/*.parquet from fieldmaps/subnational and fieldmaps/international catalogs and a Tanzania edge-extend --debug run.
-- FIELDMAPS=.. TZA_DEBUG=tmp/tza-debug/work duckdb -c ".read scripts/subnational-steps.sql"
LOAD spatial;
SET geometry_always_xy = true;
SET threads = 5;
SET VARIABLE root = getenv('FIELDMAPS');
SET VARIABLE debug = getenv('TZA_DEBUG');
SET VARIABLE delta = ST_MakeEnvelope(39.2, -7.95, 39.35, -7.8);

CREATE MACRO clip(g) AS ST_SetCRS(ST_ReducePrecision(ST_Intersection(g, ST_MakeEnvelope(-180, -90, 180, 90)), 1e-9), 'OGC:CRS84');
CREATE MACRO delta(g) AS clip(ST_Intersection(g, getvariable('delta')));

COPY (SELECT clip(geometry) AS geom FROM read_parquet(getvariable('root') || '/subnational/catalog/source/tza/tza_original.parquet'))
  TO 'catalog/subnational/original/original.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT fid, clip(ST_LineMerge(geom)) AS geom FROM read_parquet(getvariable('debug') || '/tza_original_parquet_02.parquet'))
  TO 'catalog/subnational/outlines/outlines.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT delta(geometry) AS geom FROM read_parquet(getvariable('root') || '/subnational/catalog/source/tza/tza_original.parquet')
  WHERE ST_Intersects(geometry, getvariable('delta')))
  TO 'catalog/subnational/delta/delta.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT clip(geom) AS geom FROM read_parquet(getvariable('debug') || '/tza_original_parquet_03b.parquet')
  WHERE ST_Intersects(geom, getvariable('delta')))
  TO 'catalog/subnational/points/points.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT fid, delta(geom) AS geom FROM read_parquet(getvariable('debug') || '/tza_original_parquet_04_tmp2.parquet')
  WHERE ST_Intersects(geom, getvariable('delta')))
  TO 'catalog/subnational/cells/cells.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT clip(geometry) AS geom FROM read_parquet(getvariable('root') || '/subnational/catalog/source/tza/tza_extended.parquet'))
  TO 'catalog/subnational/extended/extended.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT clip(geometry) AS geom FROM read_parquet(getvariable('root') || '/subnational/catalog/iso3/tza/adm3_polygons.parquet'))
  TO 'catalog/subnational/clipped/clipped.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (SELECT clip(geometry) AS geom FROM read_parquet(getvariable('root') || '/international/catalog/odbl/humanitarian/adm0-polygons/adm0_polygons.parquet')
  WHERE iso3 = 'TZA')
  TO 'catalog/subnational/adm0/adm0.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);

-- Fail the build on any invalid output geometry or polygon coverage.
SELECT CASE WHEN NOT bool_and(ST_IsValid(geom)) THEN error('invalid geometry in ' || filename) END
FROM read_parquet('catalog/subnational/*/*.parquet', filename = true) GROUP BY filename;
SELECT CASE WHEN ST_CoverageInvalidEdges_Agg(geom, 1e-8) IS NOT NULL THEN error('invalid coverage in ' || filename) END
FROM read_parquet(['catalog/subnational/original/original.parquet', 'catalog/subnational/delta/delta.parquet', 'catalog/subnational/cells/cells.parquet', 'catalog/subnational/extended/extended.parquet', 'catalog/subnational/clipped/clipped.parquet'], filename = true) GROUP BY filename;

-- Writes catalog/international/*/*.parquet from a fieldmaps/international checkout that has run with --debug.
-- FIELDMAPS_BUILD=../international duckdb -c ".read scripts/international-steps.sql"
LOAD spatial;
SET geometry_always_xy = true;
SET threads = 5;
SET VARIABLE build = getenv('FIELDMAPS_BUILD');

CREATE MACRO clip(g) AS ST_SetCRS(ST_ReducePrecision(ST_Intersection(g, ST_MakeEnvelope(-180, -90, 180, 90)), 1e-9), 'OGC:CRS84');

COPY (
  SELECT * FROM (SELECT clip(ST_LineMerge(geom)) AS geom FROM read_parquet(getvariable('build') || '/tmp/debug/_03_build/lsib_00.parquet'))
  WHERE NOT ST_IsEmpty(geom)
) TO 'catalog/international/lsib/lsib.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (
  SELECT * FROM (SELECT clip(ST_LineMerge(geom)) AS geom FROM read_parquet(getvariable('build') || '/inputs/adm0_lines.parquet'))
  WHERE NOT ST_IsEmpty(geom)
) TO 'catalog/international/template/template.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (
  SELECT id, clip(geom) AS geom FROM read_parquet(getvariable('build') || '/tmp/debug/osm/_03_build/points_00.parquet')
) TO 'catalog/international/points/points.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);
COPY (
  SELECT * FROM (SELECT id, clip(geom) AS geom FROM read_parquet(getvariable('build') || '/tmp/debug/osm/_03_build/voronoi_00.parquet'))
  WHERE NOT ST_IsEmpty(geom)
) TO 'catalog/international/areas/areas.parquet' (COMPRESSION ZSTD, COMPRESSION_LEVEL 15, GEOPARQUET_VERSION V2);

-- Fail the build on any invalid output geometry or polygon coverage.
SELECT CASE WHEN NOT bool_and(ST_IsValid(geom)) THEN error('invalid geometry in ' || filename) END
FROM read_parquet('catalog/international/*/*.parquet', filename = true) GROUP BY filename;
SELECT CASE WHEN ST_CoverageInvalidEdges_Agg(geom, 1e-8) IS NOT NULL THEN error('invalid coverage in ' || filename) END
FROM read_parquet(['catalog/international/areas/areas.parquet'], filename = true) GROUP BY filename;

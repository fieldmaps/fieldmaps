# Subnational build steps

Intermediate layers from the FieldMaps subnational edge-extension build for Nicaragua, Tanzania and Kenya at ADM2, shown in the Subnational story. Every collection has an `iso3` column. The finished boundaries are in `fieldmaps/subnational`.

## Collections

- `original/`: Subnational source polygons for Nicaragua, Tanzania and Kenya at ADM2. Tanzania's ADM3 source is dissolved to ADM2.
- `outlines/`: Outer edges of the original polygons, each piece keeping the polygon it came from.
- `points/`: Points placed along the outlines, each keeping its polygon.
- `cells/`: Voronoi polygons around the outline points, each keeping its point's polygon.
- `dissolved/`: Voronoi cells joined into one shape per source polygon on the outer edge.
- `extended/`: Original polygons merged with their dissolved cells, reaching past the national boundary.
- `adm0/`: FieldMaps ADM0 polygons for each country, from the OpenStreetMap-based humanitarian view.
- `clipped/`: Extended polygons clipped to the FieldMaps ADM0 boundary, as published in fieldmaps/subnational.
- `mismatch/`: Where each country's dissolved original polygons differ from its FieldMaps ADM0 polygon.

## Data access

Base URL `https://data.source.coop/fieldmaps/site/subnational/`. Each collection holds `<name>.parquet` (GeoParquet V2, CRS `OGC:CRS84`) and `<name>.pmtiles` (layer `<name>`).

## License

CC-BY-3.0-IGO, except `adm0/`, `clipped/` and `mismatch/` (ODbL-1.0). Each collection's AGENTS.md has its attribution.

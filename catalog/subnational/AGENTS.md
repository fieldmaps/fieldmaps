# Subnational build steps (Tanzania)

Intermediate layers from the FieldMaps subnational edge-extension build for Tanzania, shown in the Subnational story. The finished boundaries are in `fieldmaps/subnational`.

## Collections

- `original/`: Tanzania ADM3 polygons as published.
- `outlines/`: outer edges of the original polygons.
- `delta/`: original polygons clipped to a small area of the Rufiji delta.
- `points/`: points from the outlines in the Rufiji delta.
- `cells/`: Voronoi polygons from those points.
- `extended/`: original polygons merged with the dissolved Voronoi cells.
- `adm0/`: the FieldMaps ADM0 polygon for Tanzania.
- `clipped/`: extended polygons clipped to that ADM0 boundary.

## Data access

Base URL `https://data.source.coop/fieldmaps/site/subnational/`. Each collection holds `<name>.parquet` (GeoParquet V2, CRS `OGC:CRS84`) and `<name>.pmtiles` (layer `<name>`).

## License

CC-BY-3.0-IGO, except `adm0/` and `clipped/` (ODbL-1.0). Each collection's AGENTS.md has its attribution.

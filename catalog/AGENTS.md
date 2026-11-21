# FieldMaps site demo data

Layers behind the build-step stories on fieldmaps.io, as GeoParquet with PMTiles alongside. Each catalog holds intermediate layers from one FieldMaps pipeline.

## Catalogs

- `international/`: steps from the international boundaries build (ODbL-1.0).
- `subnational/`: steps from the subnational edge-extension build for Tanzania (CC-BY-3.0-IGO).

Each collection's AGENTS.md lists its files, columns and license.

## Data access

- Base URL: `https://data.source.coop/fieldmaps/site/`
- Each collection `<catalog>/<name>/` holds `<name>.parquet` (GeoParquet V2, CRS `OGC:CRS84`) and `<name>.pmtiles` (layer `<name>`).

## License

Catalog metadata is CC0-1.0. Data licenses are set per collection.

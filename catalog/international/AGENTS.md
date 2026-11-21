# International build steps

Intermediate layers from the FieldMaps international boundaries build, shown in the International story. The finished boundaries are in `fieldmaps/international`.

## Collections

- `lsib/`: LSIB lines, merged into continuous lines.
- `template/`: extension lines around coastal islands and inlets.
- `areas/`: lines polygonized into ADM0 areas, before clipping to land.
- `points/`: ISO3 points for each area.

## Data access

Base URL `https://data.source.coop/fieldmaps/site/international/`. Each collection holds `<name>.parquet` (GeoParquet V2, CRS `OGC:CRS84`) and `<name>.pmtiles` (layer `<name>`).

## License

ODbL-1.0. Attribution: © OpenStreetMap contributors, U.S. Department of State, FieldMaps.

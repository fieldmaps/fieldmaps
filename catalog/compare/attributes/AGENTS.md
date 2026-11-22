# Boundary comparison attributes

ADM0 attributes from every source on the comparison page, joined on the uppercased ISO3 code, with UN M49 and UNTERM as references. Built by `scripts/compare_attributes.py`; the page's Attributes table reads `attributes.json`.

## Data access

- JSON: `https://data.source.coop/fieldmaps/site/compare/attributes/attributes.json`
- Parquet: `https://data.source.coop/fieldmaps/site/compare/attributes/attributes.parquet` (same rows)
- One row per `iso3`. Columns are `{attribute}_{source}`: attributes `name`, `mapname`, `sovereign`, `status`, `region`; sources `fieldmaps`, `wp`, `overture`, `wb`, `gaul`, `gadm`, `cgaz`, `ne`, `unterm`, `m49`. A source lacking an attribute has no column for it. Several distinct values for one code are joined with ` | `.
- `count_{source}`: features with the code in that source's polygons.
- `bbox`: `[west, south, east, north]` over every source's parts; east passes 180 for codes across the antimeridian.
- `parts`: one entry per feature, `{s, id, layer, name, label, bbox}`, where `name` is the feature's name as the source's PMTiles carry it.

```sql
SELECT iso3, name_fieldmaps, name_unterm, status_unterm, region_m49
FROM 'https://data.source.coop/fieldmaps/site/compare/attributes/attributes.parquet'
WHERE name_fieldmaps IS DISTINCT FROM name_unterm;
```

## License

Each column carries its source's license; see the source collections' READMEs. M49 is from the UN Statistics Division and UNTERM from the UN terminology database.

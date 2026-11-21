import type { ExpressionSpecification, StyleSpecification } from "maplibre-gl";

const DATA = "https://data.source.coop/fieldmaps";
const ATTRIBUTION =
  '<a href="https://source.coop/fieldmaps">FieldMaps</a>, LSIB, © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';
export const pmtiles = (path: string) => ({
  type: "vector" as const,
  url: `pmtiles://${DATA}/${path}`,
  attribution: ATTRIBUTION,
});

// UN map-publication line types from the line_type tile property; dashes are in line widths.
const LINE_TYPES = {
  international: { dash: [1, 0], width: 1.5 },
  special: { dash: [4, 1.5, 1, 1.5], width: 1.5 },
  armistice: { dash: [3, 1.5], width: 1.5 },
  separation: { dash: [1, 1.5], width: 1.5 },
  autonomous: { dash: [3, 1.5], width: 1.1 },
  sovereign: { dash: [1, 0], width: 0.75 },
};

export function byType(value: (t: (typeof LINE_TYPES)[keyof typeof LINE_TYPES]) => unknown) {
  return [
    "match",
    ["get", "line_type"],
    ...Object.entries(LINE_TYPES).flatMap(([k, t]) => [k, value(t)]),
    value(LINE_TYPES.international),
  ] as unknown as ExpressionSpecification;
}

export const TOKENS = ["water", "land", "fill", "adm0", "adm1", "label"] as const;
type Colors = Record<(typeof TOKENS)[number], string>;

export function readColors(): Colors {
  const css = getComputedStyle(document.documentElement);
  return Object.fromEntries(
    TOKENS.map((t) => [t, css.getPropertyValue(`--map-${t}`).trim()]),
  ) as Colors;
}

export function buildStyle(c: Colors, opts: { labels?: boolean } = {}): StyleSpecification {
  return {
    version: 8,
    projection: { type: "globe" },
    glyphs: "https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf",
    sources: {
      adm0Polygons: pmtiles("international/odbl/humanitarian/adm0-polygons/adm0_polygons.pmtiles"),
      adm0Lines: pmtiles("international/odbl/humanitarian/adm0-lines/adm0_lines.pmtiles"),
      adm0Points: pmtiles("international/odbl/humanitarian/adm0-points/adm0_points.pmtiles"),
      adm1Lines: pmtiles("subnational/global/adm1-lines/adm1_lines.pmtiles"),
    },
    layers: [
      { id: "water", type: "background", paint: { "background-color": c.water } },
      {
        id: "land",
        type: "fill",
        source: "adm0Polygons",
        "source-layer": "adm0_polygons",
        paint: { "fill-color": c.land },
      },
      {
        id: "tint",
        type: "fill",
        source: "adm0Polygons",
        "source-layer": "adm0_polygons",
        paint: { "fill-color": c.fill, "fill-opacity": 0.06 },
      },
      {
        id: "adm1",
        type: "line",
        source: "adm1Lines",
        "source-layer": "adm1_lines",
        paint: { "line-color": c.adm1, "line-width": 0.6, "line-opacity": 0.8 },
      },
      {
        id: "adm0",
        type: "line",
        source: "adm0Lines",
        "source-layer": "adm0_lines",
        paint: {
          "line-color": c.adm0,
          "line-width": byType((t) => t.width),
          "line-dasharray": byType((t) => ["literal", t.dash]),
        },
      },
      {
        id: "labels",
        type: "symbol",
        source: "adm0Points",
        "source-layer": "adm0_points",
        minzoom: 2,
        layout: {
          visibility: opts.labels === false ? "none" : "visible",
          "text-field": ["get", "adm0_name"],
          "text-font": ["Noto Sans Regular"],
          "text-size": 11,
          "text-max-width": 8,
        },
        paint: { "text-color": c.label, "text-halo-color": c.land, "text-halo-width": 1.2 },
      },
    ],
  };
}

// Apparent globe diameter in px at zoom 0 with the default camera, measured in adm0-app.
const GLOBE_PX_AT_Z0 = 129;
const GLOBE_FIT = 0.9;

export function globeFitZoom(el: HTMLElement, fit = GLOBE_FIT) {
  return Math.log2((fit * Math.min(el.clientWidth, el.clientHeight)) / GLOBE_PX_AT_Z0);
}

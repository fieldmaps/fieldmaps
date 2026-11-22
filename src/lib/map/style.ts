import type { ExpressionSpecification } from "maplibre-gl";

const DATA = "https://data.source.coop/fieldmaps";
const ATTRIBUTION =
  '<a href="https://source.coop/fieldmaps">FieldMaps</a>, LSIB, © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';
// Dev can read the site catalog's own tiles from a local catalog/ (PUBLIC_SITE_DATA=/site-data).
const SITE_DATA = import.meta.env.DEV && import.meta.env.PUBLIC_SITE_DATA;
export const tileUrl = (path: string) =>
  SITE_DATA && path.startsWith("site/")
    ? `${location.origin}${SITE_DATA}/${path.slice("site/".length)}`
    : `${DATA}/${path}`;
export const pmtiles = (path: string, attribution = ATTRIBUTION) => ({
  type: "vector" as const,
  url: `pmtiles://${tileUrl(path)}`,
  attribution,
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

// Apparent globe diameter in px at zoom 0 with the default camera, measured in adm0-app.
const GLOBE_PX_AT_Z0 = 129;
const GLOBE_FIT = 0.9;

export function globeFitZoom(el: HTMLElement, fit = GLOBE_FIT) {
  return Math.log2((fit * Math.min(el.clientWidth, el.clientHeight)) / GLOBE_PX_AT_Z0);
}

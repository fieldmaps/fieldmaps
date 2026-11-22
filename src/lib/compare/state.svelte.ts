import { reduced } from "../map/map";

export type Slot = "a" | "b";
export type View = "fade" | Slot;

export const SOURCES = [
  {
    id: "fieldmaps",
    label: "FieldMaps",
    path: "international/odbl/humanitarian/adm0-polygons/adm0_polygons.pmtiles",
    layer: "adm0_polygons",
  },
  {
    id: "wp",
    label: "US State Dept",
    path: "site/compare/wp-polygons/wp_polygons.pmtiles",
    layer: "wp_polygons",
    attribution: '<a href="https://geodata.state.gov">U.S. Department of State</a>',
  },
  {
    id: "overture",
    label: "Overture",
    path: "site/compare/overture-polygons/overture_polygons.pmtiles",
    layer: "overture_polygons",
    attribution:
      '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="https://overturemaps.org">Overture Maps Foundation</a>',
  },
  {
    id: "wb",
    label: "World Bank",
    path: "site/compare/wb-polygons/wb_polygons.pmtiles",
    layer: "wb_polygons",
    attribution:
      '<a href="https://datacatalog.worldbank.org/search/dataset/0038272">World Bank</a>',
  },
  {
    id: "gaul",
    label: "FAO GAUL",
    path: "site/compare/gaul-polygons/gaul_polygons.pmtiles",
    layer: "gaul_polygons",
    attribution:
      '<a href="https://data.apps.fao.org/catalog/dataset/global-administrative-unit-layers-gaul">FAO GAUL 2025</a>',
  },
  {
    id: "gadm",
    label: "GADM",
    path: "site/compare/gadm-polygons/gadm_polygons.pmtiles",
    layer: "gadm_polygons",
    attribution: '<a href="https://gadm.org">GADM</a>',
  },
  {
    id: "cgaz",
    label: "geoBoundaries",
    path: "site/compare/cgaz-polygons/cgaz_polygons.pmtiles",
    layer: "cgaz_polygons",
    attribution: '<a href="https://www.geoboundaries.org">geoBoundaries</a>',
  },
  {
    id: "ne",
    label: "Natural Earth",
    path: "site/compare/ne-polygons/ne_polygons.pmtiles",
    layer: "ne_polygons",
    attribution: '<a href="https://www.naturalearthdata.com">Natural Earth</a>',
  },
] as const;
export type SourceId = (typeof SOURCES)[number]["id"];

export const VIEWS: { id: View; label: string }[] = [
  { id: "fade", label: "Fade" },
  { id: "a", label: "A" },
  { id: "b", label: "B" },
];
export const SLOTS: Slot[] = ["a", "b"];
export type Basemap = "map" | "satellite";
export const BASEMAPS: { id: Basemap; label: string }[] = [
  { id: "map", label: "Map" },
  { id: "satellite", label: "Satellite" },
];

const FADE_CYCLE_MS = 3000;
const KEY_STEP: Record<string, number> = { "[": -1, "]": 1 };

export class CompareState {
  pair = $state<Record<Slot, SourceId>>({ a: "fieldmaps", b: "wp" });
  view = $state<View>(reduced ? "a" : "fade");
  basemap = $state<Basemap>("map");
  sweep = $state(0);
  #frame = 0;

  opacities = $derived<Record<Slot, number>>(
    this.view === "fade"
      ? { a: 1 - this.sweep, b: this.sweep }
      : { a: Number(this.view === "a"), b: Number(this.view === "b") },
  );

  animate(on: boolean) {
    cancelAnimationFrame(this.#frame);
    if (!on) return;
    const start = performance.now();
    const tick = (now: number) => {
      this.sweep = (1 - Math.cos((2 * Math.PI * (now - start)) / FADE_CYCLE_MS)) / 2;
      this.#frame = requestAnimationFrame(tick);
    };
    this.#frame = requestAnimationFrame(tick);
  }

  // Picking the other slot's source swaps the two, so A and B always differ.
  pick(slot: Slot, id: SourceId) {
    const other = slot === "a" ? "b" : "a";
    if (this.pair[other] === id) this.pair[other] = this.pair[slot];
    this.pair[slot] = id;
  }

  keydown(e: KeyboardEvent) {
    // Option and AltGr stay allowed, since some layouts need them to type [ and ].
    if (e.metaKey || (e.ctrlKey && !e.altKey)) return;
    if ((e.target as Element).closest?.("input:not([type=radio]), select, textarea")) return;
    const by = KEY_STEP[e.key];
    if (by === undefined) return;
    const next = VIEWS[VIEWS.findIndex((v) => v.id === this.view) + by];
    if (next) this.view = next.id;
  }
}

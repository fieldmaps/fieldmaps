import { reduced } from "../map/map";
import { unionBox, type Part } from "./attributes";

export type Slot = "a" | "b";
export type View = "fade" | Slot;

export const SOURCES = [
  {
    id: "fieldmaps",
    code: "iso3",
    name: "adm0_name",
    label: "FieldMaps",
    path: "international/odbl/humanitarian/adm0-polygons/adm0_polygons.pmtiles",
    layer: "adm0_polygons",
    lines: {
      path: "international/odbl/humanitarian/adm0-lines/adm0_lines.pmtiles",
      layer: "adm0_lines",
    },
    voronoi: {
      path: "site/compare/fieldmaps-voronoi/fieldmaps_voronoi.pmtiles",
      layer: "fieldmaps_voronoi",
    },
  },
  {
    id: "wp",
    code: "GENC_3",
    name: "Map_Label",
    label: "US State Dept",
    path: "site/compare/wp-polygons/wp_polygons.pmtiles",
    layer: "wp_polygons",
    lines: { path: "site/compare/wp-lines/wp_lines.pmtiles", layer: "wp_lines" },
    voronoi: {
      path: "site/compare/wp-voronoi/wp_voronoi.pmtiles",
      layer: "wp_voronoi",
    },
    attribution: '<a href="https://geodata.state.gov">U.S. Department of State</a>',
  },
  {
    id: "overture",
    code: "iso3",
    name: "name",
    label: "Overture",
    path: "site/compare/overture-polygons/overture_polygons.pmtiles",
    layer: "overture_polygons",
    lines: { path: "site/compare/overture-lines/overture_lines.pmtiles", layer: "overture_lines" },
    voronoi: {
      path: "site/compare/overture-voronoi/overture_voronoi.pmtiles",
      layer: "overture_voronoi",
    },
    attribution:
      '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="https://overturemaps.org">Overture Maps Foundation</a>',
  },
  {
    id: "wb",
    code: "ISO_A3",
    name: "NAM_0",
    label: "World Bank",
    path: "site/compare/wb-polygons/wb_polygons.pmtiles",
    layer: "wb_polygons",
    lines: { path: "site/compare/wb-lines/wb_lines.pmtiles", layer: "wb_lines" },
    voronoi: {
      path: "site/compare/wb-voronoi/wb_voronoi.pmtiles",
      layer: "wb_voronoi",
    },
    attribution:
      '<a href="https://datacatalog.worldbank.org/search/dataset/0038272">World Bank</a>',
  },
  {
    id: "gaul",
    code: "ISO3_CODE",
    name: "GAUL0_NAME",
    label: "FAO GAUL",
    path: "site/compare/gaul-polygons/gaul_polygons.pmtiles",
    layer: "gaul_polygons",
    lines: { path: "site/compare/gaul-lines/gaul_lines.pmtiles", layer: "gaul_lines" },
    voronoi: {
      path: "site/compare/gaul-voronoi/gaul_voronoi.pmtiles",
      layer: "gaul_voronoi",
    },
    attribution:
      '<a href="https://data.apps.fao.org/catalog/dataset/global-administrative-unit-layers-gaul">FAO GAUL 2025</a>',
  },
  {
    id: "gadm",
    code: "iso3",
    name: "COUNTRY",
    label: "GADM",
    path: "site/compare/gadm-polygons/gadm_polygons.pmtiles",
    layer: "gadm_polygons",
    lines: { path: "site/compare/gadm-lines/gadm_lines.pmtiles", layer: "gadm_lines" },
    voronoi: {
      path: "site/compare/gadm-voronoi/gadm_voronoi.pmtiles",
      layer: "gadm_voronoi",
    },
    attribution: '<a href="https://gadm.org">GADM</a>',
  },
  {
    id: "cgaz",
    code: "shapeGroup",
    name: "shapeName",
    label: "geoBoundaries",
    path: "site/compare/cgaz-polygons/cgaz_polygons.pmtiles",
    layer: "cgaz_polygons",
    lines: { path: "site/compare/cgaz-lines/cgaz_lines.pmtiles", layer: "cgaz_lines" },
    voronoi: {
      path: "site/compare/cgaz-voronoi/cgaz_voronoi.pmtiles",
      layer: "cgaz_voronoi",
    },
    attribution: '<a href="https://www.geoboundaries.org">geoBoundaries</a>',
  },
  {
    id: "ne",
    code: "ADM0_A3",
    name: "NAME",
    label: "Natural Earth",
    path: "site/compare/ne-polygons/ne_polygons.pmtiles",
    layer: "ne_polygons",
    lines: { path: "site/compare/ne-lines/ne_lines.pmtiles", layer: "ne_lines" },
    voronoi: {
      path: "site/compare/ne-voronoi/ne_voronoi.pmtiles",
      layer: "ne_voronoi",
    },
    attribution: '<a href="https://www.naturalearthdata.com">Natural Earth</a>',
  },
] as const;
export type SourceId = (typeof SOURCES)[number]["id"];

export type Level = 0 | 1 | 2 | 3 | 4;
export type Scope = "international" | "subnational";
export const SCOPES: { id: Scope; label: string }[] = [
  { id: "international", label: "International" },
  { id: "subnational", label: "Subnational" },
];
export const LEVELS: { id: Level; label: string }[] = [1, 2, 3, 4].map((n) => ({
  id: n as Level,
  label: `Adm${n}`,
}));
export interface LevelLayer {
  path: string;
  layer: string;
}
const fieldmapsLevel = (n: number): LevelLayer => ({
  path: `subnational/global/adm${n}-polygons/adm${n}_polygons.pmtiles`,
  layer: `adm${n}_polygons`,
});
// Layers from catalog/explore, one per source and level.
const explore = (id: string, levels: number[]) =>
  Object.fromEntries(
    levels.map((n): [number, LevelLayer] => [
      n,
      {
        path: `site/explore/${id}-adm${n}-polygons/${id}_adm${n}_polygons.pmtiles`,
        layer: `${id}_adm${n}_polygons`,
      },
    ]),
  );
// Each source's polygons per admin level above 0.
export const SUBNATIONAL: Partial<Record<SourceId, Partial<Record<Level, LevelLayer>>>> = {
  fieldmaps: Object.fromEntries([1, 2, 3, 4].map((n) => [n, fieldmapsLevel(n)])),
  overture: explore("overture", [1, 2, 3]),
  wb: explore("wb", [1, 2]),
  gaul: explore("gaul", [1, 2]),
  gadm: explore("gadm", [1, 2, 3, 4]),
  cgaz: explore("cgaz", [1, 2]),
  ne: explore("ne", [1]),
};
export const hasLevel = (id: SourceId, level: Level) => level === 0 || !!SUBNATIONAL[id]?.[level];
// Map layer ids of a source at a level: the source id at adm0, "{id}-adm{n}" above.
export const layerKey = (id: SourceId, level: Level) => (level ? `${id}-adm${level}` : id);

export const VIEWS: { id: View; label: string }[] = [
  { id: "fade", label: "Fade" },
  { id: "a", label: "A" },
  { id: "b", label: "B" },
];
export const SLOTS: Slot[] = ["a", "b"];
export type Mode = "lines" | "polygons" | "voronoi";
export const MODES: { id: Mode; label: string }[] = [
  { id: "lines", label: "Lines" },
  { id: "polygons", label: "Polygons" },
  { id: "voronoi", label: "Voronoi" },
];
export type Basemap = "map" | "satellite";
export const BASEMAPS: { id: Basemap; label: string }[] = [
  { id: "map", label: "Map" },
  { id: "satellite", label: "Satellite" },
];

// A code picked on the map, optionally narrowed to some features; fly frames it.
export interface Focus {
  iso3: string;
  bbox: number[] | null;
  parts: Part[];
  fly: boolean;
}

export interface Hit {
  slot: Slot;
  label: string;
  properties: Record<string, unknown>;
}

const FADE_CYCLE_MS = 3000;
const KEY_STEP: Record<string, number> = { "[": -1, "]": 1 };

export class CompareState {
  pair = $state<Record<Slot, SourceId>>({ a: "fieldmaps", b: "wp" });
  mode = $state<Mode>("lines");
  level = $state<Level>(0);
  // The subnational level to return to from International.
  subLevel = $state<Level>(1);
  view = $state<View>(reduced ? "a" : "fade");
  basemap = $state<Basemap>("map");
  sweep = $state(0);
  hits = $state<Hit[]>([]);
  focus = $state.raw<Focus | null>(null);
  #frame = 0;

  available = $derived(SOURCES.filter((s) => hasLevel(s.id, this.level)));
  // Subnational levels draw polygons only; the adm0 pick returns with adm0.
  shownMode = $derived<Mode>(this.level ? "polygons" : this.mode);

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

  focusOn(iso3: string, bbox: number[] | null, parts: Part[], fly: boolean) {
    this.focus = {
      iso3,
      bbox: parts.length ? unionBox(parts.map((p) => p.bbox)) : bbox,
      parts,
      fly,
    };
  }

  // A slot whose source lacks the level takes the first one that has it and differs from the other slot.
  setLevel(level: Level) {
    this.level = level;
    if (level) this.subLevel = level;
    this.hits = [];
    this.focus = null;
    for (const slot of SLOTS) {
      if (hasLevel(this.pair[slot], level)) continue;
      const other = this.pair[slot === "a" ? "b" : "a"];
      const next = SOURCES.find((s) => s.id !== other && hasLevel(s.id, level));
      if (next) this.pair[slot] = next.id;
    }
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
    if (e.key === "Escape") {
      this.hits = [];
      this.focus = null;
    }
    if ((e.target as Element).closest?.("input:not([type=radio]), select, textarea")) return;
    const by = KEY_STEP[e.key];
    if (by === undefined) return;
    const next = VIEWS[VIEWS.findIndex((v) => v.id === this.view) + by];
    if (next) this.view = next.id;
  }
}

<script lang="ts">
  import * as maplibregl from "maplibre-gl";
  import { color, createMap, GLOBE, reduced } from "../map/map";
  import { SATELLITE, SATELLITE_PROTOCOL, satelliteTile } from "../map/satellite";
  import { byType, globeFitZoom, pmtiles } from "../map/style";
  import {
    SLOTS,
    SOURCES,
    type CompareState,
    type Focus,
    type Hit,
    type ItemFocus,
    type Slot,
  } from "./state.svelte";

  let {
    compare,
    inset,
    mapTab,
    listItems,
    onpick,
    onitempick,
  }: {
    compare: CompareState;
    inset: number;
    mapTab: boolean;
    listItems: string[] | null;
    onpick: (iso3: string, source: string, name: string) => void;
    onitempick: (item: string | null) => void;
  } = $props();

  const FILL_OPACITY = 0.15;
  const BASEMAP = "https://tiles.openfreemap.org/styles/positron";
  let positronIds: string[] = [];
  // Positron's own borders and country names would compete with the sources being compared.
  const hidden = (l: maplibregl.LayerSpecification) =>
    ("source-layer" in l && l["source-layer"] === "boundary") ||
    /^label_(country|state)/.test(l.id);
  // Every OSM country border, maritime ones included, with each side's adm0_l/adm0_r value.
  const OSM_COLOR = "#9e7ba6";
  const osmBorder = {
    source: "openmaptiles",
    "source-layer": "boundary",
    filter: ["==", ["get", "admin_level"], 2] as maplibregl.FilterSpecification,
  };
  const OSM_BORDERS: maplibregl.LayerSpecification[] = [
    {
      ...osmBorder,
      id: "osm-borders",
      type: "line",
      paint: { "line-color": OSM_COLOR, "line-width": 1 },
    },
    ...(["adm0_l", "adm0_r"] as const).map((side, i): maplibregl.LayerSpecification => ({
      ...osmBorder,
      id: `osm-border-${side}`,
      type: "symbol",
      layout: {
        "symbol-placement": "line",
        "symbol-spacing": 300,
        "text-field": ["get", side],
        "text-font": ["Noto Sans Regular"],
        "text-size": 11,
        "text-offset": [0, i ? 0.8 : -0.8],
      },
      paint: { "text-color": OSM_COLOR, "text-halo-color": "#ffffff", "text-halo-width": 1 },
    })),
  ];

  const LAYERS = [
    ["fill", "fill", "polygons"],
    ["line", "line", "polygons"],
    ["boundary", "line", "lines"],
    ["cell-fill", "fill", "voronoi"],
    ["cell-line", "line", "voronoi"],
  ] as const;
  const CLICK_PAD = 3;
  const FOCUS_WIDTH = 5;
  const DIM = {
    map: { color: "#ffffff", opacity: 0.7 },
    satellite: { color: "#000000", opacity: 0.55 },
  };
  const FOCUS_PAD = { top: 60, right: 40, bottom: 40, left: 320 };
  const FOCUS_MAX_ZOOM = 14;
  const MIN_FIT_PX = 200;
  const SLIDE_MS = 300;
  const DIFF = "differences";
  const DIFF_DOTS = "differences_dots";
  const DIFF_COLOR = "#7b3fa0";
  const DIFF_FILL_OPACITY = 0.45;
  // Islands draw in neutral grey, apart from both sources' colours; other items' patches in a lighter one.
  const ISLAND_COLOR = "#424242";
  const OTHER_ITEM_COLOR = "#9e9e9e";
  const ENTITY_FILL_OPACITY = 0.3;
  // "all" draws islands always and land outside Fade; in Fade, "a" and "b" each draw land in one slot's colour.
  const DIFF_SETS = ["all", "a", "b"] as const;
  const DIFF_FILLS = DIFF_SETS.map((k) => `${DIFF}-${k}-fill`);
  // Transparent, so a click finds the difference under it, Voronoi area rows included.
  const DIFF_PICK = `${DIFF}-pick`;
  type Expr = maplibregl.ExpressionSpecification;
  const ISLAND: Expr = ["==", ["get", "type"], "island"];
  // Voronoi area rows only take clicks; the sources' own Voronoi cells show the rest.
  const PATCH: Expr = ["!=", ["get", "type"], "voronoi"];
  // Land border shifts (land patches on side "both") never draw.
  const NOT_BORDER: Expr = [
    "!",
    ["all", ["==", ["get", "type"], "land"], ["==", ["get", "side"], "both"]],
  ];
  // Tiles name sides by sorted source id, so swapped means slot A holds tile side "b".
  const drawnByA = (swapped: boolean): Expr => ["==", ["get", "side"], swapped ? "b" : "a"];
  // Island rows are slot A's own islands, so only those drawn by A's tile side show.
  const ownIslands = (swapped: boolean): Expr => ["any", ["!", ISLAND], drawnByA(swapped)];
  const inItems = (ids: string[]): Expr => ["in", ["get", "item"], ["literal", ids]];
  // Focused land draws only through its entities' tint, so it never looks like a region of its own.
  const focusedLandHidden = (ids: string[]): Expr => [
    "!",
    ["all", ["==", ["get", "type"], "land"], inItems(ids)],
  ];
  const diffCommon = {
    source: DIFF,
    "source-layer": DIFF,
    layout: { visibility: "none" as const },
  };
  const DIFF_LAYERS: maplibregl.LayerSpecification[] = [
    ...DIFF_SETS.flatMap((k): maplibregl.LayerSpecification[] => [
      {
        ...diffCommon,
        id: `${DIFF}-${k}-fill`,
        type: "fill",
        paint: { "fill-color": DIFF_COLOR, "fill-opacity": ["case", ISLAND, 1, DIFF_FILL_OPACITY] },
      },
      // The white edge keeps a grey island apart from dark satellite water.
      {
        ...diffCommon,
        id: `${DIFF}-${k}-line`,
        type: "line",
        paint: { "line-color": DIFF_COLOR, "line-width": ["case", ISLAND, 1, 0.5] },
      },
    ]),
    { ...diffCommon, id: DIFF_PICK, type: "fill", paint: { "fill-opacity": 0 } },
  ];
  // One point per island difference, above source lines; its edge thins out by z12 into its island.
  const DOTS_LAYER: maplibregl.LayerSpecification = {
    id: DIFF_DOTS,
    source: DIFF_DOTS,
    "source-layer": DIFF_DOTS,
    layout: { visibility: "none" },
    type: "circle",
    paint: {
      "circle-color": ISLAND_COLOR,
      "circle-radius": 4,
      "circle-stroke-color": "#ffffff",
      "circle-stroke-width": ["interpolate", ["linear"], ["zoom"], 8, 1, 12, 0],
    },
  };
  // Each source's whole Voronoi cells for a focused difference or code, so islands joined to a mainland read as one.
  const entityLayers = (type: "fill" | "line") =>
    SOURCES.map((s): maplibregl.LayerSpecification => ({
      source: `${s.id}-voronoi`,
      "source-layer": s.voronoi.layer,
      layout: { visibility: "none" },
      ...(type === "fill"
        ? {
            id: `${s.id}-entity-fill`,
            type: "fill" as const,
            paint: { "fill-opacity": ENTITY_FILL_OPACITY },
          }
        : { id: `${s.id}-entity`, type: "line" as const, paint: { "line-width": FOCUS_WIDTH } }),
    }));
  const codeOf = (s: (typeof SOURCES)[number]): maplibregl.ExpressionSpecification => [
    "upcase",
    ["to-string", ["coalesce", ["get", s.code], ""]],
  ];

  let container: HTMLDivElement;
  let map = $state.raw<maplibregl.Map | null>(null);

  $effect(() => {
    maplibregl.addProtocol(SATELLITE_PROTOCOL, satelliteTile);
    const { map: m, destroy } = createMap({
      container,
      center: [20, 10],
      zoom: globeFitZoom(container),
      attributionControl: { compact: true },
      style: BASEMAP,
      transformStyle: (_, next) => {
        const base = next!.layers.filter((l) => !hidden(l));
        positronIds = base.filter((l) => l.layout?.visibility !== "none").map((l) => l.id);
        return {
          ...next!,
          ...GLOBE,
          // Fade sets opacity every frame, so easing would only make it lag.
          transition: { duration: 0, delay: 0 },
          sources: {
            ...next!.sources,
            satellite: SATELLITE,
            ...Object.fromEntries(
              SOURCES.flatMap((s) => {
                const attribution = "attribution" in s ? s.attribution : undefined;
                return [
                  [s.id, pmtiles(s.path, attribution)],
                  [`${s.id}-lines`, pmtiles(s.lines.path, attribution)],
                  [`${s.id}-voronoi`, pmtiles(s.voronoi.path, attribution)],
                ];
              }),
            ),
            [DIFF]: pmtiles("site/compare/differences/differences.pmtiles"),
            [DIFF_DOTS]: pmtiles("site/compare/differences-dots/differences_dots.pmtiles"),
          },
          layers: [
            ...base,
            {
              id: "satellite",
              type: "raster",
              source: "satellite",
              layout: { visibility: "none" },
            },
            ...OSM_BORDERS,
            ...entityLayers("fill"),
            ...DIFF_LAYERS,
            ...SOURCES.flatMap((s): maplibregl.LayerSpecification[] => {
              const common = {
                source: s.id,
                "source-layer": s.layer,
                layout: { visibility: "none" as const },
              };
              return [
                {
                  ...common,
                  id: `${s.id}-fill`,
                  type: "fill",
                  paint: { "fill-opacity": FILL_OPACITY },
                },
                { ...common, id: `${s.id}-line`, type: "line", paint: { "line-width": 3 } },
                // Transparent, so a click finds the country under it in Lines mode too.
                { ...common, id: `${s.id}-pick`, type: "fill", paint: { "fill-opacity": 0 } },
                {
                  ...common,
                  source: `${s.id}-lines`,
                  "source-layer": s.lines.layer,
                  id: `${s.id}-boundary`,
                  type: "line",
                  paint: {
                    "line-width": 3,
                    "line-dasharray": byType((t) => ["literal", t.dash]),
                  },
                },
                ...(["fill", "line"] as const).map((type): maplibregl.LayerSpecification => ({
                  ...common,
                  source: `${s.id}-voronoi`,
                  "source-layer": s.voronoi.layer,
                  id: `${s.id}-cell-${type}`,
                  type,
                  paint: type === "fill" ? { "fill-opacity": FILL_OPACITY } : { "line-width": 3 },
                })),
              ];
            }),
            // Every dim sits under every outline, so one source's dim never covers the other's outline.
            ...(["fill", "line"] as const).flatMap((type) =>
              SOURCES.map((s): maplibregl.LayerSpecification => ({
                source: s.id,
                "source-layer": s.layer,
                layout: { visibility: "none" },
                ...(type === "fill"
                  ? { id: `${s.id}-dim`, type, paint: { "fill-color": DIM.map.color } }
                  : { id: `${s.id}-focus`, type, paint: { "line-width": FOCUS_WIDTH } }),
              })),
            ),
            ...entityLayers("line"),
            DOTS_LAYER,
          ],
        };
      },
    });
    m.once("load", () => {
      map = m;
      m.on("click", (e) => {
        // On a Geometry list, a Voronoi click picks the difference there, a patch before its area.
        if (!mapTab && compare.mode === "voronoi" && listItems) {
          const found = m
            .queryRenderedFeatures(around(e.point), { layers: [DIFF_PICK] })
            .sort(
              (x, y) =>
                Number(x.properties.type === "voronoi") - Number(y.properties.type === "voronoi"),
            );
          onitempick(found[0]?.properties.item ?? null);
          compare.hits = query(m, e.point);
          return;
        }
        compare.hits = query(m, e.point);
        // Voronoi clicks on the Map tab only report each source's cell, so the patches stay unobscured.
        if (mapTab && compare.mode === "voronoi") return;
        // Rendered order puts later sources first; A's feature should win.
        const ids = SLOTS.map((slot) => `${compare.pair[slot]}-pick`);
        const hit = m
          .queryRenderedFeatures(e.point, { layers: ids })
          .sort((x, y) => ids.indexOf(x.layer.id) - ids.indexOf(y.layer.id))[0];
        const s = hit && SOURCES.find((s) => `${s.id}-pick` === hit.layer.id);
        if (s)
          onpick(
            String(hit.properties[s.code] ?? "").toUpperCase(),
            s.id,
            String(hit.properties[s.name] ?? ""),
          );
      });
    });
    return () => {
      destroy();
      map = null;
      maplibregl.removeProtocol(SATELLITE_PROTOCOL);
    };
  });

  // A first, each slot's line before its polygon; tiles split a feature, so repeats are dropped.
  // Voronoi reports the cell, which also answers clicks on water.
  function around({ x, y }: maplibregl.Point): [maplibregl.PointLike, maplibregl.PointLike] {
    return [
      [x - CLICK_PAD, y - CLICK_PAD],
      [x + CLICK_PAD, y + CLICK_PAD],
    ];
  }

  // The fill a difference draws in, as the difference layers set it.
  function diffColor(f: maplibregl.MapGeoJSONFeature): string {
    const items = compare.item?.ids;
    if (items && !items.includes(f.properties.item)) return OTHER_ITEM_COLOR;
    if (f.properties.type === "island") return ISLAND_COLOR;
    const k = f.layer.id.slice(DIFF.length + 1, -"-fill".length);
    if (k === "all") return DIFF_COLOR;
    const swapped = compare.pair.a > compare.pair.b;
    return color(`--compare-${(k === "b") !== swapped ? "b" : "a"}`);
  }

  // Voronoi also reports the differences under the click.
  function query(m: maplibregl.Map, point: maplibregl.Point): Hit[] {
    const { x, y } = point;
    const lines = compare.mode === "lines";
    const box = around(point);
    const diffs: Hit[] =
      compare.mode === "voronoi"
        ? m.queryRenderedFeatures(box, { layers: DIFF_FILLS }).map((f) => ({
            slot: null,
            label: "Difference",
            color: diffColor(f),
            properties: { type: f.properties.type, km2: Number(f.properties.km2).toFixed(2) },
          }))
        : [];
    const hits = SLOTS.flatMap((slot) => {
      const s = SOURCES.find((s) => s.id === compare.pair[slot])!;
      const found = [
        ...(lines ? m.queryRenderedFeatures(box, { layers: [`${s.id}-boundary`] }) : []),
        ...m.queryRenderedFeatures([x, y], {
          layers: [compare.mode === "voronoi" ? `${s.id}-cell-fill` : `${s.id}-pick`],
        }),
      ];
      return found.map((f) => {
        const kind = f.layer.id.endsWith("-boundary") ? "line" : "polygon";
        return { slot, label: lines ? `${s.label} ${kind}` : s.label, properties: f.properties };
      });
    });
    const all = [...hits, ...diffs];
    const keys = all.map((h) => JSON.stringify(h));
    return all.filter((_, i) => keys.indexOf(keys[i]) === i);
  }

  $effect(() => {
    void [compare.mode, compare.view, compare.pair.a, compare.pair.b];
    compare.hits = [];
  });

  $effect(() => {
    if (!map) return;
    for (const s of SOURCES) {
      const slot = SLOTS.find((k) => compare.pair[k] === s.id);
      map.setLayoutProperty(`${s.id}-pick`, "visibility", slot ? "visible" : "none");
      for (const [layer, type, mode] of LAYERS) {
        const shown = slot && mode === compare.mode;
        map.setLayoutProperty(`${s.id}-${layer}`, "visibility", shown ? "visible" : "none");
        if (shown)
          map.setPaintProperty(`${s.id}-${layer}`, `${type}-color`, color(`--compare-${slot}`));
      }
    }
  });

  $effect(() => {
    if (!map) return;
    for (const slot of SLOTS) {
      const id = compare.pair[slot];
      const o = compare.opacities[slot];
      map.setPaintProperty(`${id}-focus`, "line-opacity", o);
      map.setPaintProperty(`${id}-dim`, "fill-opacity", DIM[compare.basemap].opacity * o);
      map.setPaintProperty(`${id}-entity`, "line-opacity", o);
      map.setPaintProperty(`${id}-entity-fill`, "fill-opacity", ENTITY_FILL_OPACITY * o);
      for (const [layer, type] of LAYERS)
        map.setPaintProperty(
          `${id}-${layer}`,
          `${type}-opacity`,
          type === "fill" ? FILL_OPACITY * o : o,
        );
    }
  });

  // Fade outlines and dims both sources at their own opacity, so a code missing from one leaves no undimmed hole.
  $effect(() => {
    if (!map) return;
    // Voronoi tints a focused code's cells instead of outlining its land.
    const focus = compare.mode === "voronoi" ? null : compare.focus;
    const shown = compare.view === "fade" ? SLOTS : [compare.view];
    const dim = DIM[compare.basemap];
    for (const s of SOURCES) {
      const slot = SLOTS.find((k) => compare.pair[k] === s.id);
      const on = !!focus && !!slot && shown.includes(slot);
      map.setLayoutProperty(`${s.id}-focus`, "visibility", on ? "visible" : "none");
      map.setLayoutProperty(`${s.id}-dim`, "visibility", on ? "visible" : "none");
      if (!on) continue;
      const code: maplibregl.FilterSpecification = ["==", codeOf(s), focus.iso3];
      const names = focus.parts.filter((p) => p.layer === s.id).map((p) => p.name);
      map.setFilter(
        `${s.id}-focus`,
        names.length ? ["all", code, ["in", ["get", s.name], ["literal", names]]] : code,
      );
      map.setPaintProperty(`${s.id}-focus`, "line-color", color(`--compare-${slot}`));
      map.setFilter(`${s.id}-dim`, ["!=", codeOf(s), focus.iso3]);
      map.setPaintProperty(`${s.id}-dim`, "fill-color", dim.color);
    }
  });

  // Each pick frames once, after the layout settles so a pane that just opened has its final size.
  // Shows the pair's patches in Voronoi, limited to listItems; Voronoi areas stay pickable either way.
  $effect(() => {
    if (!map) return;
    const pair = compare.mode === "voronoi" ? compare.diffPair : null;
    const swapped = compare.pair.a > compare.pair.b;
    const items = compare.item?.ids ?? null;
    const split = compare.view === "fade";
    const byPair: Expr = ["==", ["get", "pair"], pair ?? ""];
    const inList: Expr[] = listItems ? [inItems(listItems)] : [];
    map.setLayoutProperty(DIFF_PICK, "visibility", pair ? "visible" : "none");
    map.setFilter(DIFF_PICK, [
      "all",
      byPair,
      NOT_BORDER,
      ownIslands(swapped),
      ["any", ["!", PATCH], ...(listItems ? inList : [true])],
    ]);
    // Every island dot of the pair shows until a difference is picked, then only its own.
    map.setLayoutProperty(DIFF_DOTS, "visibility", pair ? "visible" : "none");
    map.setFilter(DIFF_DOTS, [
      "all",
      byPair,
      drawnByA(swapped),
      ...inList,
      ...(items ? [inItems(items)] : []),
    ]);
    for (const k of DIFF_SETS) {
      const shown = !!pair && (k === "all" || split);
      const kinds: Expr[] = k === "all" ? (split ? [ISLAND] : []) : [["!", ISLAND]];
      const slot: Slot = (k === "b") !== swapped ? "b" : "a";
      const land = k === "all" ? DIFF_COLOR : color(`--compare-${slot}`);
      for (const type of ["fill", "line"] as const) {
        const id = `${DIFF}-${k}-${type}`;
        map.setLayoutProperty(id, "visibility", shown ? "visible" : "none");
        if (!shown) continue;
        map.setFilter(id, [
          "all",
          byPair,
          NOT_BORDER,
          PATCH,
          ownIslands(swapped),
          ...kinds,
          ...inList,
          ...(items ? [focusedLandHidden(items)] : []),
        ]);
        const edge = type === "line" ? "#ffffff" : ISLAND_COLOR;
        const base: Expr = ["case", ISLAND, edge, land];
        const other: Expr = [
          "case",
          ISLAND,
          edge === "#ffffff" ? edge : OTHER_ITEM_COLOR,
          OTHER_ITEM_COLOR,
        ];
        map.setPaintProperty(
          id,
          `${type}-color`,
          items ? ["case", inItems(items), base, other] : base,
        );
      }
    }
  });

  // Each slot's patches crossfade with its own layers; plain numbers only, since Fade sets this every frame.
  $effect(() => {
    if (!map || compare.mode !== "voronoi" || compare.view !== "fade") return;
    const swapped = compare.pair.a > compare.pair.b;
    for (const k of ["a", "b"] as const) {
      const o = compare.opacities[(k === "b") !== swapped ? "b" : "a"];
      map.setPaintProperty(`${DIFF}-${k}-fill`, "fill-opacity", DIFF_FILL_OPACITY * o);
      map.setPaintProperty(`${DIFF}-${k}-line`, "line-opacity", o);
    }
  });

  // An item merging several entities of one source joins their codes and names with "; ".
  const oneOf = (key: string, value: unknown): Expr =>
    value == null
      ? ["==", ["get", key], null]
      : ["in", ["get", key], ["literal", String(value).split("; ")]];

  // The cells to tint per source: a difference's entities, or a focused code narrowed to picked parts.
  function cellFilter(
    s: (typeof SOURCES)[number],
    item: ItemFocus | null,
    focus: Focus | null,
  ): maplibregl.FilterSpecification | null {
    if (item) {
      const ents = (item.entities[s.id] ?? []).filter(([c, n]) => c != null || n != null);
      if (!ents.length) return null;
      return [
        "any",
        ...ents.map(([c, n]) => ["all", oneOf(s.code, c), oneOf(s.name, n)]),
      ] as maplibregl.FilterSpecification;
    }
    if (!focus) return null;
    const byCode: maplibregl.FilterSpecification = ["==", codeOf(s), focus.iso3];
    const names = focus.parts.filter((p) => p.layer === s.id).map((p) => p.name);
    return names.length ? ["all", byCode, ["in", ["get", s.name], ["literal", names]]] : byCode;
  }

  // Voronoi tints each drawn source's cells for the focused difference or code.
  $effect(() => {
    if (!map) return;
    const voronoi = compare.mode === "voronoi";
    for (const s of SOURCES) {
      const slot = SLOTS.find((k) => compare.pair[k] === s.id);
      const filter = voronoi && slot ? cellFilter(s, compare.item, compare.focus) : null;
      for (const [id, type] of [
        [`${s.id}-entity`, "line"],
        [`${s.id}-entity-fill`, "fill"],
      ] as const) {
        map.setLayoutProperty(id, "visibility", filter ? "visible" : "none");
        if (!filter || !slot) continue;
        map.setFilter(id, filter);
        map.setPaintProperty(id, `${type}-color`, color(`--compare-${slot}`));
      }
    }
  });

  function frame(target: Focus | ItemFocus | null) {
    if (!map || !target?.fly || !target.bbox) return;
    const [m, bbox] = [map, target.bbox as [number, number, number, number]];
    // fitBounds adds this to the pane's padding, and does nothing when the sum is wider than the canvas.
    const free = m.getContainer().clientWidth - inset - FOCUS_PAD.left - FOCUS_PAD.right;
    const roomy = free >= MIN_FIT_PX;
    const padding = roomy ? FOCUS_PAD : { ...FOCUS_PAD, left: FOCUS_PAD.right };
    requestAnimationFrame(() => m.fitBounds(bbox, { padding, maxZoom: FOCUS_MAX_ZOOM }));
  }
  $effect(() => frame(compare.focus));
  $effect(() => frame(compare.item));

  // A pane over the map's right edge pads the camera instead of resizing the canvas.
  $effect(() => {
    if (!map) return;
    map.easeTo({
      padding: { top: 0, bottom: 0, left: 0, right: inset },
      duration: reduced ? 0 : SLIDE_MS,
    });
  });

  $effect(() => {
    if (!map) return;
    const satellite = compare.basemap === "satellite";
    for (const id of positronIds)
      map.setLayoutProperty(id, "visibility", satellite ? "none" : "visible");
    map.setLayoutProperty("satellite", "visibility", satellite ? "visible" : "none");
  });

  $effect(() => {
    compare.animate(compare.view === "fade");
    return () => compare.animate(false);
  });
</script>

<svelte:window onkeydown={(e) => compare.keydown(e)} />

<div class="map" bind:this={container}></div>

<style>
  .map {
    position: absolute;
    inset: 0;
  }
  .map :global(.maplibregl-canvas) {
    cursor: pointer;
  }
  .map :global(.maplibregl-ctrl-bottom-right) {
    right: var(--inset);
    transition: right 300ms cubic-bezier(0.2, 0, 0, 1);
  }
</style>

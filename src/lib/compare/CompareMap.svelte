<script lang="ts">
  import * as maplibregl from "maplibre-gl";
  import { color, createMap, GLOBE, reduced } from "../map/map";
  import { SATELLITE, SATELLITE_PROTOCOL, satelliteTile } from "../map/satellite";
  import { byType, globeFitZoom, pmtiles } from "../map/style";
  import { SLOTS, SOURCES, type CompareState, type Hit } from "./state.svelte";

  let {
    compare,
    inset,
    onpick,
  }: {
    compare: CompareState;
    inset: number;
    onpick: (iso3: string, source: string, name: string) => void;
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
  const SLIDE_MS = 300;
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
          ],
        };
      },
    });
    m.once("load", () => {
      map = m;
      m.on("click", (e) => {
        compare.hits = query(m, e.point);
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
  function query(m: maplibregl.Map, { x, y }: maplibregl.Point): Hit[] {
    const lines = compare.mode === "lines";
    const box: [maplibregl.PointLike, maplibregl.PointLike] = [
      [x - CLICK_PAD, y - CLICK_PAD],
      [x + CLICK_PAD, y + CLICK_PAD],
    ];
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
    const keys = hits.map((h) => JSON.stringify(h));
    return hits.filter((_, i) => keys.indexOf(keys[i]) === i);
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
    const focus = compare.focus;
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
  $effect(() => {
    const focus = compare.focus;
    if (!map || !focus?.fly || !focus.bbox) return;
    const [m, bbox] = [map, focus.bbox as [number, number, number, number]];
    requestAnimationFrame(() => m.fitBounds(bbox, { padding: FOCUS_PAD, maxZoom: FOCUS_MAX_ZOOM }));
  });

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

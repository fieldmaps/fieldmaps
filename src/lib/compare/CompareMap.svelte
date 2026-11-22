<script lang="ts">
  import * as maplibregl from "maplibre-gl";
  import { color, createMap, GLOBE } from "../map/map";
  import { SATELLITE, SATELLITE_PROTOCOL, satelliteTile } from "../map/satellite";
  import { globeFitZoom, pmtiles } from "../map/style";
  import { SLOTS, SOURCES, type CompareState } from "./state.svelte";

  let { compare }: { compare: CompareState } = $props();

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
              SOURCES.map((s) => [
                s.id,
                pmtiles(s.path, "attribution" in s ? s.attribution : undefined),
              ]),
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
              ];
            }),
          ],
        };
      },
    });
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }));
    m.once("load", () => (map = m));
    return () => {
      destroy();
      map = null;
      maplibregl.removeProtocol(SATELLITE_PROTOCOL);
    };
  });

  $effect(() => {
    if (!map) return;
    for (const s of SOURCES) {
      const slot = SLOTS.find((k) => compare.pair[k] === s.id);
      for (const type of ["fill", "line"] as const) {
        map.setLayoutProperty(`${s.id}-${type}`, "visibility", slot ? "visible" : "none");
        if (slot)
          map.setPaintProperty(`${s.id}-${type}`, `${type}-color`, color(`--compare-${slot}`));
      }
    }
  });

  $effect(() => {
    if (!map) return;
    for (const slot of SLOTS) {
      const id = compare.pair[slot];
      const o = compare.opacities[slot];
      map.setPaintProperty(`${id}-fill`, "fill-opacity", FILL_OPACITY * o);
      map.setPaintProperty(`${id}-line`, "line-opacity", o);
    }
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
</style>

<script lang="ts">
  import type * as maplibregl from "maplibre-gl";
  import Story from "../Story.svelte";
  import { color, GLOBE } from "../map/map";
  import { byType, globeFitZoom, pmtiles } from "../map/style";

  type Layer =
    | "original"
    | "original-line"
    | "outlines"
    | "delta"
    | "delta-line"
    | "points"
    | "cells"
    | "cells-line"
    | "extended"
    | "extended-line"
    | "clipped"
    | "clipped-line"
    | "adm0"
    | "world"
    | "world-adm1"
    | "world-adm0";
  type Bounds = [number, number, number, number];

  const TANZANIA: Bounds = [29.3, -11.8, 40.5, -0.9];
  const DELTA: Bounds = [39.2, -7.95, 39.35, -7.8];
  const STEPS: { title: string; text: string; bounds?: Bounds; layers: Layer[] }[] = [
    {
      title: "Original input",
      text: "The United Republic of Tanzania is used in this example as it contains many elements that have been difficult to resolve in the past: lakes along international boundaries, internal water bodies shared by multiple areas, groups of islands, etc.",
      bounds: TANZANIA,
      layers: ["original", "original-line"],
    },
    {
      title: "Polygon to line",
      text: "The first part extracts outlines from the polygon, first by dissolving all polygons together, then by taking the intersection between the outline of the dissolved and the original layer. By intersecting these two together, it retains attribute information of where segments originate from.",
      bounds: TANZANIA,
      layers: ["original", "outlines"],
    },
    {
      title: "Line to point",
      text: "The first set of points are taken from all vertices that make up a line. However, for certain areas like winding rivers and deltas, this is an insufficient level of detail to properly center the resulting voronoi. Lines are therefore split up into segments based on an automatically-chosen distance, with points taken at the breaks between segments.",
      bounds: DELTA,
      layers: ["delta", "delta-line", "points"],
    },
    {
      title: "Point to Voronoi",
      text: "For country sized inputs, there may be hundreds of thousands, if not millions of individual voronoi polygons created in this step. Because each individual section retains attribute information of what polygon it originated from, they can be dissolved together to a simplified output.",
      bounds: DELTA,
      layers: ["cells", "cells-line", "delta", "delta-line", "points"],
    },
    {
      title: "Polygon-Voronoi merge",
      text: "The original polygon is overlayed in a union with the voronoi. Boundaries from the inner area are kept from the original, dissolved with polygons containing matching attributes from the outside area.",
      bounds: TANZANIA,
      layers: ["extended", "original", "extended-line"],
    },
    {
      title: "Matching to ADM0",
      text: "This resolves edge differences between different levels of administrative boundaries, where some layers included water bodies but others did not.",
      bounds: TANZANIA,
      layers: ["clipped", "clipped-line", "adm0"],
    },
    {
      title: "Global",
      text: "A multi-source data processing pipeline creates global edge-matched administrative boundary layers.",
      layers: ["world", "world-adm1", "world-adm0"],
    },
  ];
  const WORLD_CENTER: [number, number] = [30, 0];
  const site = (name: string) => pmtiles(`site/subnational/${name}/${name}.pmtiles`);
  const line = (id: Layer, source: string, c: string, width: number) => ({
    id,
    type: "line" as const,
    source,
    "source-layer": source,
    paint: { "line-color": color(c), "line-width": width },
  });
  const fill = (id: Layer, source: string, c: string) => ({
    id,
    type: "fill" as const,
    source,
    "source-layer": source,
    paint: { "fill-color": color(c) },
  });

  const options = (): Omit<maplibregl.MapOptions, "container"> => ({
    bounds: TANZANIA,
    attributionControl: { compact: true },
    style: {
      version: 8,
      ...GLOBE,
      sources: {
        original: site("original"),
        outlines: site("outlines"),
        delta: site("delta"),
        points: site("points"),
        cells: site("cells"),
        extended: site("extended"),
        clipped: site("clipped"),
        adm0: site("adm0"),
        world: pmtiles("international/odbl/humanitarian/adm0-polygons/adm0_polygons.pmtiles"),
        worldLines: pmtiles("international/odbl/humanitarian/adm0-lines/adm0_lines.pmtiles"),
        worldAdm1: pmtiles("subnational/global/adm1-lines/adm1_lines.pmtiles"),
      },
      layers: [
        { id: "sea", type: "background", paint: { "background-color": color("--sky") } },
        { ...fill("world", "world", "--white"), "source-layer": "adm0_polygons" },
        { ...line("world-adm1", "worldAdm1", "--fold", 0.6), "source-layer": "adm1_lines" },
        {
          ...line("world-adm0", "worldLines", "--ink", 0.8),
          "source-layer": "adm0_lines",
          paint: {
            "line-color": color("--ink"),
            "line-width": byType((t) => (t.width * 0.8) / 1.5),
            "line-dasharray": byType((t) => ["literal", t.dash]),
          },
        },
        fill("cells", "cells", "--paper"),
        fill("extended", "extended", "--paper"),
        fill("original", "original", "--white"),
        fill("delta", "delta", "--white"),
        fill("clipped", "clipped", "--white"),
        line("cells-line", "cells", "--fold-deep", 0.4),
        line("extended-line", "extended", "--fold-deep", 0.4),
        line("original-line", "original", "--fold-deep", 0.4),
        line("delta-line", "delta", "--fold-deep", 0.8),
        line("clipped-line", "clipped", "--fold-deep", 0.4),
        line("outlines", "outlines", "--ink", 1),
        line("adm0", "adm0", "--ink", 1.2),
        {
          id: "points",
          type: "circle",
          source: "points",
          "source-layer": "points",
          paint: { "circle-color": color("--ink"), "circle-radius": 1.5 },
        },
      ],
    },
  });
  const camera = (map: maplibregl.Map, step: (typeof STEPS)[number]) =>
    step.bounds
      ? map.cameraForBounds(step.bounds, { padding: 24 })!
      : { center: WORLD_CENTER, zoom: globeFitZoom(map.getContainer(), 0.9) };
  const move = (map: maplibregl.Map, step: (typeof STEPS)[number], animate: boolean) => {
    if (animate) map.flyTo({ ...camera(map, step), duration: 2000 });
    else map.jumpTo(camera(map, step));
  };
</script>

<Story title="Subnational Boundaries" steps={STEPS} {options} {move} />

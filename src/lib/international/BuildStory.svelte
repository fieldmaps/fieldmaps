<script lang="ts">
  import type * as maplibregl from "maplibre-gl";
  import Story from "../Story.svelte";
  import { color, GLOBE } from "../map/map";
  import { byType, globeFitZoom, pmtiles } from "../map/style";

  type Layer = "land" | "areas-line" | "lsib" | "template" | "points" | "outlines" | "labels";

  const STEPS: { title: string; text: string; center: [number, number]; layers: Layer[] }[] = [
    {
      title: "LSIB lines",
      text: "Political boundaries are delineated with an extension of the U.S. Department of State Large Scale International Boundaries (LSIB) layer.",
      center: [15, 15],
      layers: ["lsib"],
    },
    {
      title: "Extensions",
      text: "Manual edits to polygons introduce the possibility of topology errors from gaps and overlaps, something much less likely to occur when editing divisions as a single line. Small manual adjustments are commonly made around coastal islands and inlets.",
      center: [35, 15],
      layers: ["lsib", "template"],
    },
    {
      title: "Points",
      text: "A companion point layer provides the ISO3 code for the area represented by lines.",
      center: [55, 15],
      layers: ["lsib", "template", "points"],
    },
    {
      title: "Polygons",
      text: "Lines are polygonized into an ADM0 layer suitable for intersecting with land. Points are joined by location to add attribute information.",
      center: [80, 10],
      layers: ["land", "areas-line", "points"],
    },
    {
      title: "Outputs",
      text: "Polygons are clipped to OpenStreetMap coastlines. Lines follow only boundaries over land, and points mark each polygon's visual center, for placing labels.",
      center: [105, 10],
      layers: ["land", "outlines", "labels"],
    },
  ];
  const DOWNLOAD = "https://source.coop/fieldmaps/international";
  const adm0 = "international/odbl/humanitarian/adm0";
  const site = (name: string) => pmtiles(`site/international/${name}/${name}.pmtiles`);

  const options = (container: HTMLDivElement): Omit<maplibregl.MapOptions, "container"> => ({
    center: STEPS[0].center,
    zoom: globeFitZoom(container, 0.9),
    attributionControl: { compact: true },
    style: {
      version: 8,
      glyphs: `${location.origin}/fonts/{fontstack}/{range}.pbf`,
      ...GLOBE,
      sources: {
        land: pmtiles(`${adm0}-polygons/adm0_polygons.pmtiles`),
        lsib: site("lsib"),
        template: site("template"),
        points: site("points"),
        areas: site("areas"),
        outlines: pmtiles(`${adm0}-lines/adm0_lines.pmtiles`),
        labels: pmtiles(`${adm0}-points/adm0_points.pmtiles`),
      },
      layers: [
        { id: "sea", type: "background", paint: { "background-color": color("--sky") } },
        {
          id: "land",
          type: "fill",
          source: "land",
          "source-layer": "adm0_polygons",
          paint: { "fill-color": color("--white") },
        },
        {
          id: "areas-line",
          type: "line",
          source: "areas",
          "source-layer": "areas",
          paint: { "line-color": color("--fold-deep"), "line-width": 0.8 },
        },
        {
          id: "template",
          type: "line",
          source: "template",
          "source-layer": "template",
          paint: { "line-color": color("--white"), "line-width": 1.2 },
        },
        {
          id: "lsib",
          type: "line",
          source: "lsib",
          "source-layer": "lsib",
          paint: { "line-color": color("--white"), "line-width": 0.8 },
        },
        {
          id: "outlines",
          type: "line",
          source: "outlines",
          "source-layer": "adm0_lines",
          paint: {
            "line-color": color("--ink"),
            "line-width": byType((t) => (t.width * 0.8) / 1.5),
            "line-dasharray": byType((t) => ["literal", t.dash]),
          },
        },
        {
          id: "points",
          type: "symbol",
          source: "points",
          "source-layer": "points",
          layout: {
            "text-field": ["slice", ["get", "id"], 0, 3],
            "text-font": ["public-sans-semibold"],
            "text-size": 10,
          },
          paint: {
            "text-color": color("--ink"),
            "text-halo-color": color("--white"),
            "text-halo-width": 1.2,
          },
        },
        {
          id: "labels",
          type: "symbol",
          source: "labels",
          "source-layer": "adm0_points",
          filter: ["==", ["get", "status_nm"], "State"],
          layout: {
            "text-field": ["get", "adm0_name"],
            "text-font": ["public-sans-semibold"],
            "text-size": 11,
            "text-max-width": 7,
          },
          paint: {
            "text-color": color("--ink"),
            "text-halo-color": color("--white"),
            "text-halo-width": 1.2,
          },
        },
      ],
    },
  });
  const move = (map: maplibregl.Map, step: (typeof STEPS)[number], animate: boolean) => {
    if (animate) map.easeTo({ center: step.center, duration: 1200 });
    else map.jumpTo({ center: step.center, zoom: globeFitZoom(map.getContainer(), 0.9) });
  };
</script>

<Story
  title="International Boundaries"
  tagline="Country boundaries from high-resolution international border lines, clipped to OpenStreetMap coastlines."
  steps={STEPS}
  {options}
  {move}
>
  {#snippet intro()}{@render actions()}{/snippet}
  {#snippet outro()}{@render actions()}{/snippet}
</Story>

{#snippet actions()}
  <div class="actions">
    <a class="button" href={DOWNLOAD}>Download</a>
  </div>
{/snippet}

<style>
  .actions {
    display: flex;
    gap: 0.75rem;
  }
</style>

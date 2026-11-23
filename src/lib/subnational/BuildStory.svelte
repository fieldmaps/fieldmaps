<script lang="ts">
  import type * as maplibregl from "maplibre-gl";
  import Story from "../Story.svelte";
  import Segmented from "../compare/Segmented.svelte";
  import { color, FADE_MS, GLOBE } from "../map/map";
  import { byType, globeFitZoom, pmtiles } from "../map/style";

  type Layer =
    | "neighbours"
    | "original"
    | "original-line"
    | "gap"
    | "gap-soft"
    | "spill"
    | "outlines"
    | "points"
    | "cells"
    | "cells-line"
    | "dissolved"
    | "dissolved-line"
    | "extended"
    | "extended-line"
    | "clipped"
    | "clipped-line"
    | "adm0"
    | "world"
    | "world-adm3"
    | "world-adm0"
    | "world-adm0-top";
  type Bounds = [number, number, number, number];
  type Camera = "globe" | "country" | "gaps" | "spills" | "inlet" | "points";
  type Step = { title: string; text: string; camera: Camera; layers: Layer[]; caption?: string };
  type Iso3 = "NIC" | "TZA" | "KEN";
  type Spot = { bounds: Bounds; place: string };
  type Country = {
    name: string;
    bounds: Bounds;
    center: [number, number];
    gaps: Spot;
    spills: Spot;
    // Where the build steps zoom in, when it differs from the gaps spot.
    inlet?: Spot;
    points: [number, number];
  };

  const COUNTRIES: Record<Iso3, Country> = {
    NIC: {
      name: "Nicaragua",
      bounds: [-87.7, 10.7, -82.7, 15.03],
      center: [-85, 12.8],
      gaps: { bounds: [-86.4, 10.9, -84.7, 12.6], place: "Lake Nicaragua and Lake Managua" },
      spills: { bounds: [-83.26, 14.9, -83.14, 15.0], place: "Cabo Gracias a Dios" },
      points: [-85.88, 11.707],
    },
    TZA: {
      name: "Tanzania",
      bounds: [29.3, -11.8, 40.5, -0.95],
      center: [35, -6],
      gaps: { bounds: [31.2, -3.3, 34.3, -0.7], place: "Lake Victoria" },
      spills: {
        bounds: [30.7, -2.45, 30.95, -2.2],
        place: "Kagera River on the border with Rwanda",
      },
      points: [32.7746, -2.9935],
    },
    KEN: {
      name: "Kenya",
      bounds: [33.9, -4.75, 41.95, 5.45],
      center: [38, 0.5],
      gaps: { bounds: [33.95, 4.15, 34.45, 4.65], place: "Border with South Sudan" },
      spills: { bounds: [34.2, 4.0, 36.6, 5.6], place: "Ilemi Triangle, a disputed area" },
      inlet: { bounds: [40.6, -2.4, 41.7, -1.5], place: "Lamu archipelago" },
      points: [40.7691, -1.9449],
    },
  };

  const SOURCE: Layer[] = ["neighbours", "original", "original-line"];
  const WORLD: Layer[] = ["world", "world-adm3", "world-adm0"];
  const STEPS: Step[] = [
    {
      title: "Original input",
      text: "Each country publishes its own subnational boundaries. Here they sit on top of the international boundaries that FieldMaps uses for every country. The two rarely line up.",
      camera: "country",
      layers: [...SOURCE, "world-adm0"],
    },
    {
      title: "Gaps",
      text: "Sources often leave water or border strips out. These holes are shown in red and fall in no area. A point inside one can't be assigned to anyone.",
      camera: "gaps",
      layers: [...SOURCE, "gap", "adm0", "world-adm0-top"],
    },
    {
      title: "Overlaps",
      text: "Elsewhere the source reaches past the national boundary. These overlaps are shown in orange. They cover a neighbour's land, the sea or a disputed area.",
      camera: "spills",
      layers: [...SOURCE, "gap-soft", "spill", "adm0", "world-adm0-top"],
    },
    {
      title: "Edge-matching",
      text: "One process fixes both problems. Areas on the outer edge grow out to fill the gaps. The result is then cut to the national boundary. That cut removes the overlaps.",
      camera: "country",
      layers: [...SOURCE, "gap", "spill", "adm0"],
    },
    {
      title: "Polygon to line",
      text: "The outer edge of the source is traced as a line. Each piece of the line keeps the area it came from.",
      camera: "country",
      layers: ["neighbours", "original", "outlines"],
    },
    {
      title: "Line to point",
      text: "Points are placed along that line. Each point carries its area.",
      camera: "points",
      layers: ["neighbours", "original", "points"],
    },
    {
      title: "Point to Voronoi",
      text: "Each point claims all the space closer to it than to any other point. The cells reach out across the gaps.",
      camera: "inlet",
      layers: ["neighbours", "cells", "cells-line", "original"],
    },
    {
      title: "Cells to areas",
      text: "Cells from the same area join into one shape. Areas facing each other across a gap meet halfway.",
      camera: "inlet",
      layers: ["neighbours", "dissolved", "dissolved-line", "original", "original-line"],
    },
    {
      title: "Extended areas",
      text: "Each area is merged with its cells and now reaches past the national boundary. Inside the source's own edge nothing changes.",
      camera: "country",
      layers: ["neighbours", "extended", "extended-line"],
    },
    {
      title: "Clip",
      text: "The extended areas are cut to the national boundary. Every gap is now filled. Every overlap is gone.",
      camera: "country",
      layers: ["neighbours", "clipped", "clipped-line", "world-adm0", "adm0"],
    },
    {
      title: "Global",
      text: "The same process runs for every country. Subnational areas fit together edge to edge worldwide.",
      camera: "globe",
      layers: WORLD,
    },
  ];
  const BEFORE: Step = { title: "", text: "", camera: "globe", layers: [] };

  let iso3: Iso3 = $state("NIC");
  const country = $derived(COUNTRIES[iso3]);
  const ISO3 = Object.keys(COUNTRIES) as Iso3[];
  const sideways = (d: -1 | 1) =>
    (iso3 = ISO3[Math.min(Math.max(ISO3.indexOf(iso3) + d, 0), ISO3.length - 1)]);
  const spot = (camera: "gaps" | "spills" | "inlet" | "points") =>
    camera === "inlet" || camera === "points" ? (country.inlet ?? country.gaps) : country[camera];
  const steps = $derived(
    STEPS.map((s) => ({
      ...s,
      caption:
        s.camera === "globe" || s.camera === "country"
          ? undefined
          : `${spot(s.camera).place}, ${country.name}`,
    })),
  );

  const DOWNLOAD = "https://source.coop/fieldmaps/subnational";
  const ATTRIBUTION =
    '<a href="https://source.coop/fieldmaps">FieldMaps</a>, GADM, OCHA FISS, Tanzania NBS, OCHA ROSA, IEBC, OCHA ROSEA, © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';
  const site = (name: string) => pmtiles(`site/subnational/${name}/${name}.pmtiles`, ATTRIBUTION);
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
  const worldAdm0 = (id: Layer) => ({
    id,
    type: "line" as const,
    source: "worldLines",
    "source-layer": "adm0_lines",
    paint: {
      "line-color": color("--ink"),
      "line-width": byType((t) => (t.width * 0.8) / 1.5),
      "line-dasharray": byType((t) => ["literal", t.dash]),
    },
  });
  const kind = (id: Layer, c: string) => ({
    ...fill(id, "mismatch", c),
    filter: ["==", ["get", "kind"], id] as maplibregl.FilterSpecification,
  });
  // Colours cycle by area id, so pieces from neighbouring areas usually differ.
  const AREA_COLORS = [
    "#1b9e77",
    "#8c6bb1",
    "#e7298a",
    "#66a61e",
    "#01665e",
    "#a6761d",
    "#2b2b27",
    "#6a3d9a",
  ];
  // Light tints of the same colours for area fills.
  const AREA_TINTS = [
    "#a4d8c9",
    "#d1c4e0",
    "#f5a9d0",
    "#c2dba5",
    "#99c2bf",
    "#dbc8a5",
    "#aaaaa9",
    "#c3b1d7",
  ];
  const areaColor = (colors: string[]) =>
    [
      "match",
      ["%", ["to-number", ["get", "fid"]], colors.length],
      ...colors.flatMap((c, i) => [i, c]),
      colors[0],
    ] as unknown as maplibregl.ExpressionSpecification;
  const byArea = areaColor(AREA_COLORS);
  const SITE_SOURCES = [
    "original",
    "mismatch",
    "outlines",
    "points",
    "cells",
    "dissolved",
    "extended",
    "clipped",
    "adm0",
  ];

  const globe = (el: HTMLElement) => ({ center: country.center, zoom: globeFitZoom(el, 0.9) });

  const options = (container: HTMLDivElement): Omit<maplibregl.MapOptions, "container"> => ({
    ...globe(container),
    attributionControl: { compact: true },
    style: {
      version: 8,
      ...GLOBE,
      sources: {
        ...Object.fromEntries(SITE_SOURCES.map((s) => [s, site(s)])),
        world: pmtiles("international/odbl/humanitarian/adm0-polygons/adm0_polygons.pmtiles"),
        worldLines: pmtiles("international/odbl/humanitarian/adm0-lines/adm0_lines.pmtiles"),
        worldAdm3: pmtiles("subnational/global/adm3-lines/adm3_lines.pmtiles"),
      },
      layers: [
        { id: "sea", type: "background", paint: { "background-color": color("--sky") } },
        { ...fill("world", "world", "--white"), "source-layer": "adm0_polygons" },
        { ...fill("neighbours", "world", "--paper-light"), "source-layer": "adm0_polygons" },
        { ...line("world-adm3", "worldAdm3", "--fold", 0.6), "source-layer": "adm3_lines" },
        worldAdm0("world-adm0"),
        { ...fill("cells", "cells", "--paper"), paint: { "fill-color": areaColor(AREA_TINTS) } },
        fill("dissolved", "dissolved", "--paper"),
        fill("extended", "extended", "--white"),
        // Cell borders sit under the original land so they only show beyond it.
        line("cells-line", "cells", "--fold-deep", 0.3),
        line("dissolved-line", "dissolved", "--fold-deep", 0.6),
        fill("original", "original", "--white"),
        fill("clipped", "clipped", "--white"),
        kind("gap", "--gap"),
        { ...kind("gap", "--gap-soft"), id: "gap-soft" },
        kind("spill", "--spill"),
        // Drawn over the overlaps so disputed claim lines stay visible.
        worldAdm0("world-adm0-top"),
        line("extended-line", "extended", "--fold-deep", 0.6),
        line("original-line", "original", "--fold-deep", 0.6),
        line("clipped-line", "clipped", "--fold-deep", 0.6),
        {
          ...line("outlines", "outlines", "--ink", 4),
          paint: { "line-color": byArea, "line-width": 4 },
        },
        line("adm0", "adm0", "--ink", 1.4),
        {
          id: "points",
          type: "circle",
          source: "points",
          "source-layer": "points",
          paint: { "circle-color": byArea, "circle-radius": 3.5 },
        },
      ],
    },
  });

  // Show only the selected country's data, and every other country as a neighbour.
  const filter = (map: maplibregl.Map) => {
    const own: maplibregl.FilterSpecification = ["==", ["get", "iso3"], iso3];
    for (const layer of map.getStyle()?.layers ?? []) {
      if (!("source" in layer)) continue;
      if (layer.id === "neighbours") map.setFilter(layer.id, ["!=", ["get", "iso3"], iso3]);
      else if (SITE_SOURCES.includes(layer.source))
        map.setFilter(
          layer.id,
          layer.source === "mismatch"
            ? ["all", own, ["==", ["get", "kind"], layer.id.replace("-soft", "")]]
            : own,
        );
    }
  };
  // About 2.6 km across, so the outline points (about 22 m apart) show one by one.
  const around = ([x, y]: [number, number]): Bounds => [x - 0.012, y - 0.012, x + 0.012, y + 0.012];
  const camera = (map: maplibregl.Map, step: Step) => {
    const bounds =
      step.camera === "country"
        ? country.bounds
        : step.camera === "globe"
          ? undefined
          : step.camera === "points"
            ? around(country.points)
            : spot(step.camera).bounds;
    return bounds ? map.cameraForBounds(bounds, { padding: 24 })! : globe(map.getContainer());
  };
  // Zoom and content never change together: every move swaps the layers, then flies once they have faded.
  let place = "";
  let flight: ReturnType<typeof setTimeout> | undefined;
  const move = (map: maplibregl.Map, step: Step, animate: boolean) => {
    // An interrupted flight never reached its place, so the next move flies even to the same one.
    if (flight !== undefined || map.isMoving()) place = "";
    clearTimeout(flight);
    flight = undefined;
    map.stop();
    filter(map);
    const next = `${iso3} ${step.camera}`;
    const flies = animate && next !== place;
    place = next;
    const target = camera(map, step);
    if (!animate) map.jumpTo(target);
    else if (flies)
      flight = setTimeout(() => {
        flight = undefined;
        map.flyTo({ ...target, duration: 2000 });
      }, FADE_MS);
  };
</script>

<Story
  title="Subnational Boundaries"
  tagline="Each country's own admin boundaries, edge-matched to the international boundaries with no gaps or overlaps."
  {steps}
  before={BEFORE}
  refresh={iso3}
  {options}
  {move}
  {sideways}
>
  {#snippet controls()}
    <Segmented
      label="Country"
      options={ISO3.map((id) => ({ id, label: COUNTRIES[id].name }))}
      current={iso3}
      pick={(id) => (iso3 = id)}
    />
  {/snippet}
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

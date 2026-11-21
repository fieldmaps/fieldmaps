<script lang="ts">
  import ScrollHint from "../ScrollHint.svelte";
  import * as maplibregl from "maplibre-gl";
  import "maplibre-gl/dist/maplibre-gl.css";
  import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
  import { Protocol } from "pmtiles";
  import { stepKeys } from "../keys";
  import { globeFitZoom, pmtiles } from "../map/style";

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
  const FADE = { duration: 600, delay: 0 };
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const css = getComputedStyle(document.documentElement);
  const color = (name: string) => css.getPropertyValue(name).trim();

  let container: HTMLDivElement;
  let steps: HTMLElement[] = $state([]);
  let active = $state(-1);

  $effect(() => {
    maplibregl.setWorkerUrl(workerUrl);
    const protocol = new Protocol();
    maplibregl.addProtocol("pmtiles", protocol.tile);
    const adm0 = "international/odbl/humanitarian/adm0";
    const site = (name: string) => pmtiles(`site/international/${name}/${name}.pmtiles`);
    const map = new maplibregl.Map({
      container,
      interactive: false,
      center: STEPS[0].center,
      zoom: globeFitZoom(container, 0.9),
      attributionControl: { compact: true },
      style: {
        version: 8,
        glyphs: `${location.origin}/fonts/{fontstack}/{range}.pbf`,
        projection: { type: "globe" },
        sky: { "atmosphere-blend": 0 },
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
            paint: { "line-color": color("--ink"), "line-width": 0.8 },
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

    const opacity: Record<string, string[]> = {
      fill: ["fill-opacity"],
      line: ["line-opacity"],
      circle: ["circle-opacity", "circle-stroke-opacity"],
      symbol: ["text-opacity"],
    };
    const show = (i: number, animate: boolean) => {
      // Before step 1, show the finished product at step 1's camera.
      const step = STEPS[Math.max(i, 0)];
      const layers = i < 0 ? STEPS[STEPS.length - 1].layers : step.layers;
      for (const layer of map.getStyle().layers) {
        if (layer.type === "background") continue;
        const on = layers.includes(layer.id as Layer) ? 1 : 0;
        for (const prop of opacity[layer.type]) {
          map.setPaintProperty(
            layer.id,
            `${prop}-transition`,
            animate ? FADE : { duration: 0, delay: 0 },
          );
          map.setPaintProperty(layer.id, prop, on);
        }
        // Transparent symbols still block other labels, so hidden ones are switched off.
        if (layer.type === "symbol")
          map.setLayoutProperty(layer.id, "visibility", on ? "visible" : "none");
      }
      if (animate) map.easeTo({ center: step.center, duration: 1200 });
      else map.jumpTo({ center: step.center });
    };
    let ready = false;
    map.once("style.load", () => {
      ready = true;
      show(active, false);
    });

    const observer = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) active = steps.indexOf(e.target as HTMLElement);
          else if (e.target === steps[0] && e.boundingClientRect.top > e.rootBounds!.bottom)
            active = -1;
          else continue;
          if (ready) show(active, !reduced);
        }
      },
      { rootMargin: "-45% 0px -45% 0px" },
    );
    steps.forEach((s) => observer.observe(s));
    const removeKeys = stepKeys(steps, () => active, reduced);
    const resize = new ResizeObserver(() => {
      map.resize();
      map.setZoom(globeFitZoom(container, 0.9));
    });
    resize.observe(container);
    return () => {
      removeKeys();
      observer.disconnect();
      resize.disconnect();
      map.remove();
      maplibregl.removeProtocol("pmtiles");
    };
  });
</script>

<ScrollHint />
<section class="story" data-snap>
  <div class="globe">
    <div class="map" bind:this={container}></div>
  </div>
  <div class="steps">
    <div class="intro">
      <h1>International Boundaries</h1>
      <a class="button" href="https://source.coop/fieldmaps/international">Download</a>
    </div>
    {#each STEPS as step, i (step.title)}
      <article class="step" class:active={i === active} bind:this={steps[i]}>
        <h2>{step.title}</h2>
        <p>{step.text}</p>
        {#if i === STEPS.length - 1}
          <a class="button" href="https://source.coop/fieldmaps/international">Download</a>
        {/if}
      </article>
    {/each}
  </div>
</section>

<style>
  .story {
    display: grid;
    grid-template-columns: minmax(18rem, 1fr) 1.6fr;
    grid-template-areas: "steps globe";
    --inset: max(1.5rem, calc(50vw - 36rem));
  }
  .globe {
    grid-area: globe;
    position: sticky;
    top: var(--header-h);
    height: calc(100dvh - var(--header-h));
  }
  .map {
    width: 100%;
    height: 100%;
  }
  .steps {
    grid-area: steps;
    padding: 0 2rem 0 var(--inset);
  }
  .intro {
    scroll-snap-align: start;
    display: flex;
    flex-direction: column;
    padding-block: 30vh;
  }
  h1 {
    margin: 0;
    font-size: 2.5rem;
  }
  .step {
    scroll-snap-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 80vh;
    opacity: 0.35;
    transition: opacity 0.4s;
  }
  .step.active {
    opacity: 1;
  }
  .step:last-child {
    min-height: calc(100dvh - var(--header-h));
  }
  h2 {
    margin: 0 0 0.5rem;
    font-size: 1.4rem;
  }
  .step p {
    margin: 0;
    max-width: 30rem;
    font-size: 1.1rem;
    line-height: 1.55;
    color: var(--ink-soft);
  }
  .button {
    align-self: flex-start;
    margin-top: 1rem;
    padding: 0.6rem 1rem;
    border: 1px solid var(--ink);
    background: var(--ink);
    color: var(--white);
    font-weight: 600;
    text-decoration: none;
    transition: background-color 0.2s;
  }
  .button:hover {
    background: var(--ink-soft);
  }
  @media (max-width: 900px) {
    .story {
      grid-template-columns: 1fr;
      grid-template-areas: "all";
    }
    .globe {
      grid-area: all;
      height: 70dvh;
    }
    .steps {
      grid-area: all;
      z-index: 1;
      padding: 0 1rem;
    }
    .intro {
      padding-top: 72dvh;
      padding-bottom: 0;
    }
    .step {
      opacity: 1;
      min-height: 90vh;
      justify-content: flex-end;
    }
    .step h2,
    .step p {
      background: var(--paper-light);
      padding: 0.5rem 0.75rem;
    }
  }
</style>

<script lang="ts">
  import ScrollHint from "../ScrollHint.svelte";
  import * as maplibregl from "maplibre-gl";
  import "maplibre-gl/dist/maplibre-gl.css";
  import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
  import { Protocol } from "pmtiles";
  import { stepKeys } from "../keys";
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
    const map = new maplibregl.Map({
      container,
      interactive: false,
      bounds: TANZANIA,
      attributionControl: { compact: true },
      style: {
        version: 8,
        projection: { type: "globe" },
        sky: { "atmosphere-blend": 0 },
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

    const opacity: Record<string, string[]> = {
      fill: ["fill-opacity"],
      line: ["line-opacity"],
      circle: ["circle-opacity", "circle-stroke-opacity"],
    };
    const camera = (step: (typeof STEPS)[number]) =>
      step.bounds
        ? map.cameraForBounds(step.bounds, { padding: 24 })!
        : { center: WORLD_CENTER, zoom: globeFitZoom(container, 0.9) };
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
      }
      if (animate) map.flyTo({ ...camera(step), duration: 2000 });
      else map.jumpTo(camera(step));
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
      map.jumpTo(camera(STEPS[Math.max(active, 0)]));
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
    <h1>Subnational Boundaries</h1>
    {#each STEPS as step, i (step.title)}
      <article class="step" class:active={i === active} bind:this={steps[i]}>
        <h2>{step.title}</h2>
        <p>{step.text}</p>
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
  h1 {
    scroll-snap-align: start;
    margin: 0;
    padding-block: 30vh;
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
    h1 {
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

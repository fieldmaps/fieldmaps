<script lang="ts">
  import * as maplibregl from "maplibre-gl";
  import "maplibre-gl/dist/maplibre-gl.css";
  import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
  import { Protocol } from "pmtiles";
  import { untrack } from "svelte";
  import { globeFitZoom, pmtiles } from "../map/style";

  const START = -85;
  const DEGREES = 127;
  const LAT = 20;
  const GAP = 32;
  const EDGE = 24;
  // The globe sits right of the text and buttons on wide screens, below them on phones, never overlapping.
  const layout = () => {
    const w = container.clientWidth;
    const h = container.clientHeight;
    if (innerWidth <= 900) {
      const box = slot.getBoundingClientRect();
      const cy = box.top - container.getBoundingClientRect().top + box.height / 2;
      const r = Math.min(w * 0.43, box.height / 2);
      return { left: 0, top: Math.max(0, 2 * cy - h), fit: (2 * r) / Math.min(w, h) };
    }
    const x0 = container.getBoundingClientRect().left;
    const textRight = Math.max(...[text, links].map((e) => e.getBoundingClientRect().right));
    const start = textRight - x0 + GAP;
    const r = Math.min((h * 1.1) / 2, (w - start - EDGE) / 2);
    return { left: Math.max(0, 2 * (start + r) - w), top: 0, fit: (2 * r) / Math.min(w, h) };
  };
  // Pixels of wheel or swipe for the full turn.
  const DISTANCE = 600;
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const css = getComputedStyle(document.documentElement);
  const color = (name: string) => css.getPropertyValue(name).trim();

  let container: HTMLDivElement;
  let text: HTMLDivElement;
  let links: HTMLDivElement;
  let slot: HTMLDivElement;
  let progress = $state(reduced ? 1 : 0);
  const intl = $derived(1 - clamp((progress - 0.35) / 0.15));
  const sub = $derived(clamp((progress - 0.45) / 0.15));
  const swap = $derived(clamp((progress - 0.35) / 0.25));
  const name = $derived(swap < 0.5 ? "international" : "subnational");

  const clamp = (t: number) => Math.min(1, Math.max(0, t));

  $effect(() => {
    maplibregl.setWorkerUrl(workerUrl);
    const protocol = new Protocol();
    maplibregl.addProtocol("pmtiles", protocol.tile);
    const map = new maplibregl.Map({
      container,
      interactive: false,
      center: [START + DEGREES * untrack(() => progress), LAT],
      zoom: globeFitZoom(container, layout().fit),
      attributionControl: { compact: true },
      style: {
        version: 8,
        projection: { type: "globe" },
        sky: { "atmosphere-blend": 0 },
        sources: {
          adm0: pmtiles("international/odbl/humanitarian/adm0-polygons/adm0_polygons.pmtiles"),
          adm1: pmtiles("subnational/global/adm1-lines/adm1_lines.pmtiles"),
        },
        layers: [
          { id: "sea", type: "background", paint: { "background-color": color("--sky") } },
          {
            id: "land",
            type: "fill",
            source: "adm0",
            "source-layer": "adm0_polygons",
            paint: { "fill-color": color("--white") },
          },
          {
            id: "adm1",
            type: "line",
            source: "adm1",
            "source-layer": "adm1_lines",
            paint: {
              "line-color": color("--fold"),
              "line-width": 0.6,
              "line-opacity": 0,
              "line-opacity-transition": { duration: 0 },
            },
          },
          {
            id: "adm0",
            type: "line",
            source: "adm0",
            "source-layer": "adm0_polygons",
            paint: { "line-color": color("--ink"), "line-width": 0.8 },
          },
        ],
      },
    });

    let frame = 0;
    let shown = -1;
    const tick = () => {
      frame = requestAnimationFrame(tick);
      if (Math.abs(progress - shown) < 0.0005) return;
      shown = progress;
      map.setCenter([START + DEGREES * progress, LAT]);
      map.setPaintProperty("adm1", "line-opacity", clamp((progress - 0.2) / 0.5));
    };
    const step = (px: number) => {
      if (!reduced) progress = clamp(progress + px / DISTANCE);
    };
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      step(e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY);
    };
    let touchY = 0;
    const onTouchStart = (e: TouchEvent) => (touchY = e.touches[0].clientY);
    const onTouchMove = (e: TouchEvent) => {
      e.preventDefault();
      step(touchY - e.touches[0].clientY);
      touchY = e.touches[0].clientY;
    };
    const KEYS: Record<string, number> = {
      ArrowDown: 60,
      ArrowUp: -60,
      PageDown: 300,
      PageUp: -300,
      " ": 300,
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key in KEYS) step(KEYS[e.key]);
    };
    addEventListener("wheel", onWheel, { passive: false });
    addEventListener("touchstart", onTouchStart, { passive: true });
    addEventListener("touchmove", onTouchMove, { passive: false });
    addEventListener("keydown", onKey);
    map.once("load", () => (frame = requestAnimationFrame(tick)));
    const resize = new ResizeObserver(() => {
      map.resize();
      const { left, top, fit } = layout();
      map.setPadding({ left, top, right: 0, bottom: 0 });
      map.setZoom(globeFitZoom(container, fit));
    });
    resize.observe(container);
    resize.observe(text);
    return () => {
      removeEventListener("wheel", onWheel);
      removeEventListener("touchstart", onTouchStart);
      removeEventListener("touchmove", onTouchMove);
      removeEventListener("keydown", onKey);
      cancelAnimationFrame(frame);
      resize.disconnect();
      map.remove();
      maplibregl.removeProtocol("pmtiles");
    };
  });
</script>

<section class="stage">
  <div class="text" bind:this={text}>
    <h1>FieldMaps</h1>
    <p class="caption">
      <span style:opacity={intl}>International Boundaries</span>
      <span style:opacity={sub}>Subnational Boundaries</span>
    </p>
  </div>
  <div class="map" bind:this={container}></div>
  <div class="slot" bind:this={slot}></div>
  <div class="links" bind:this={links}>
    <a class="button slide-0" href="/{name}/" style:--t={swap}>Methodology</a>
    <a class="button slide-1" href="https://source.coop/fieldmaps/{name}" style:--t={swap}>
      Download
    </a>
  </div>
</section>

<style>
  .stage {
    display: grid;
    grid-template-columns: minmax(18rem, 1fr) 2fr;
    grid-template-rows: 1fr auto auto 1fr;
    grid-template-areas: ". ." "text ." "links ." ". .";
    column-gap: 2rem;
    height: calc(100dvh - var(--header-h));
    --inset: max(1.5rem, calc(50vw - 36rem));
    overflow: hidden;
    overscroll-behavior: none;
  }
  .text {
    grid-area: text;
    justify-self: start;
    margin-left: var(--inset);
    z-index: 1;
  }
  .map {
    grid-area: 1 / 1 / -1 / -1;
    min-height: 0;
  }
  .links {
    grid-area: links;
    align-self: start;
    justify-self: start;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
    margin: 2rem 0 0 var(--inset);
    z-index: 1;
  }
  .button {
    padding: 0.75rem 1.5rem;
    background: var(--ink);
    color: var(--white);
    font-weight: 600;
    text-align: center;
    text-decoration: none;
    transition: background-color 0.2s;
  }
  .slide-0 {
    grid-area: 1 / 1;
    transform: translateY(calc(var(--t) * (100% + 0.75rem)));
  }
  .slide-1 {
    grid-area: 2 / 2;
    transform: translateY(calc(var(--t) * -1 * (100% + 0.75rem)));
  }
  .button:hover {
    background: var(--ink-soft);
  }
  .slot {
    display: none;
  }
  h1 {
    margin: 0 0 0.5rem;
    font-size: 3rem;
  }
  .caption {
    display: grid;
    margin: 0;
    font-size: 1.25rem;
    color: var(--ink-soft);
  }
  .caption span {
    grid-area: 1 / 1;
  }
  @media (max-width: 900px) {
    .stage {
      grid-template-columns: 1fr;
      grid-template-rows: 1fr auto auto 1fr min(calc(0.86 * (100vw - 2rem)), 50dvh) 1fr;
      grid-template-areas: "." "text" "links" "." "slot" ".";
      padding: 1.5rem 1rem;
      text-align: center;
      --inset: 0px;
    }
    .text {
      justify-self: center;
    }
    .slot {
      display: block;
      grid-area: slot;
    }
    h1 {
      font-size: 2rem;
    }
    .caption {
      font-size: 1.05rem;
    }
    .stage .links {
      justify-self: center;
      margin: 1.5rem 0 0;
    }
  }
</style>

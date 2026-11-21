<script lang="ts">
  import ScrollHint from "../ScrollHint.svelte";
  import * as maplibregl from "maplibre-gl";
  import "maplibre-gl/dist/maplibre-gl.css";
  import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
  import { Protocol } from "pmtiles";
  import { untrack } from "svelte";
  import { direction } from "../keys";
  import { byType, globeFitZoom, pmtiles } from "../map/style";

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
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const css = getComputedStyle(document.documentElement);
  const color = (name: string) => css.getPropertyValue(name).trim();

  let container: HTMLDivElement;
  let text: HTMLDivElement;
  let links: HTMLDivElement;
  let slot: HTMLDivElement;
  let progress = $state(0);
  const name = $derived(progress < 0.5 ? "international" : "subnational");

  const clamp = (t: number) => Math.min(1, Math.max(0, t));

  const TABS = [
    { id: "international", label: "International", to: 0 },
    { id: "subnational", label: "Subnational", to: 1 },
  ] as const;
  const tabs: HTMLButtonElement[] = $state([]);

  const maxScroll = () => document.documentElement.scrollHeight - innerHeight;
  const select = (to: number) =>
    scrollTo({ top: to * maxScroll(), behavior: reduced ? "instant" : "smooth" });
  const onScroll = () => (progress = clamp(scrollY / Math.max(1, maxScroll())));
  const onTabKey = (e: KeyboardEvent) => {
    const d = direction(e);
    const next = d ? (d < 0 ? 0 : 1) : { Home: 0, End: 1 }[e.key];
    if (next === undefined) return;
    e.preventDefault();
    tabs[next].focus();
    select(TABS[next].to);
  };

  $effect(() => {
    onScroll();
    maplibregl.setWorkerUrl(workerUrl);
    const protocol = new Protocol();
    maplibregl.addProtocol("pmtiles", protocol.tile);
    const map = new maplibregl.Map({
      container,
      interactive: false,
      center: [START + DEGREES * untrack(() => progress), LAT],
      zoom: globeFitZoom(container, layout().fit),
      attributionControl: { compact: true },
      fadeDuration: 0,
      style: {
        version: 8,
        glyphs: `${location.origin}/fonts/{fontstack}/{range}.pbf`,
        projection: { type: "globe" },
        sky: { "atmosphere-blend": 0 },
        sources: {
          adm0: pmtiles("international/odbl/humanitarian/adm0-polygons/adm0_polygons.pmtiles"),
          adm0Lines: pmtiles("international/odbl/humanitarian/adm0-lines/adm0_lines.pmtiles"),
          adm1: pmtiles("subnational/global/adm1-lines/adm1_lines.pmtiles"),
          labels: pmtiles("international/odbl/humanitarian/adm0-points/adm0_points.pmtiles"),
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
            source: "adm0Lines",
            "source-layer": "adm0_lines",
            paint: {
              "line-color": color("--ink"),
              "line-width": byType((t) => (t.width * 0.8) / 1.5),
              "line-dasharray": byType((t) => ["literal", t.dash]),
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
              "text-opacity-transition": { duration: 0 },
            },
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
      map.setPaintProperty("labels", "text-opacity", 1 - clamp((progress - 0.2) / 0.3));
    };
    const onKey = (e: KeyboardEvent) => {
      if ((e.target as Element).closest?.("[role=tablist]")) return;
      const d = direction(e);
      if (!d) return;
      e.preventDefault();
      select(d < 0 ? 0 : 1);
    };
    addEventListener("scroll", onScroll, { passive: true });
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
      removeEventListener("scroll", onScroll);
      removeEventListener("keydown", onKey);
      cancelAnimationFrame(frame);
      resize.disconnect();
      map.remove();
      maplibregl.removeProtocol("pmtiles");
    };
  });
</script>

<ScrollHint />
<div class="track" data-snap>
  <div class="snap"></div>
  <section class="stage">
    <div class="text" bind:this={text}>
      <h1>FieldMaps</h1>
      <div class="tabs" role="tablist" aria-label="Boundary set">
        {#each TABS as tab, i (tab.id)}
          <button
            bind:this={tabs[i]}
            id="tab-{tab.id}"
            role="tab"
            aria-selected={name === tab.id}
            aria-controls="globe-panel"
            tabindex={name === tab.id ? 0 : -1}
            onclick={() => select(tab.to)}
            onkeydown={onTabKey}
          >
            {tab.label}
          </button>
        {/each}
      </div>
    </div>
    <div class="map" bind:this={container}></div>
    <div class="slot" bind:this={slot}></div>
    <div
      class="links"
      id="globe-panel"
      role="tabpanel"
      aria-labelledby="tab-{name}"
      bind:this={links}
    >
      {#each TABS as tab (tab.id)}
        <a class="button" class:off={name !== tab.id} href="/{tab.id}/">Methodology</a>
      {/each}
      {#each TABS as tab (tab.id)}
        <a class="button" class:off={name !== tab.id} href="https://source.coop/fieldmaps/{tab.id}">
          Download
        </a>
      {/each}
    </div>
  </section>
  <div class="spacer"></div>
</div>

<style>
  .track {
    position: relative;
  }
  .snap,
  .spacer {
    height: calc(100dvh - var(--header-h));
    scroll-snap-align: end;
  }
  .snap {
    position: absolute;
    inset: 0 0 auto;
  }
  .stage {
    position: sticky;
    top: var(--header-h);
    display: grid;
    grid-template-columns: minmax(18rem, 1fr) 2fr;
    grid-template-rows: 1fr auto auto 1fr;
    grid-template-areas: ". ." "text ." "links ." ". .";
    column-gap: 2rem;
    height: calc(100dvh - var(--header-h));
    --inset: max(1.5rem, calc(50vw - 36rem));
    --w: 20rem;
    overflow: hidden;
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
    row-gap: 0.75rem;
    width: var(--w);
    max-width: 100%;
    margin: 0.75rem 0 0 var(--inset);
    z-index: 1;
  }
  .button {
    padding: 0.6rem 1rem;
    border: 1px solid var(--ink);
    background: var(--ink);
    color: var(--white);
    font-weight: 600;
    text-align: center;
    text-decoration: none;
    transition:
      background-color 0.2s,
      opacity 0.2s,
      visibility 0.2s;
  }
  .button:hover {
    background: var(--ink-soft);
  }
  .slot {
    display: none;
  }
  .tabs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    width: var(--w);
    max-width: 100%;
    margin-top: 1rem;
    border: 1px solid var(--ink);
  }
  .tabs button {
    padding: 0.6rem 1rem;
    border: 0;
    background: none;
    font: inherit;
    font-weight: 600;
    color: var(--ink-soft);
    white-space: nowrap;
    cursor: pointer;
  }
  .tabs button[aria-selected="true"] {
    background: var(--ink);
    color: var(--white);
  }
  .button.off {
    visibility: hidden;
    opacity: 0;
  }
  h1 {
    margin: 0 0 0.5rem;
    font-size: 3rem;
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
    .tabs {
      margin-inline: auto;
    }
    .slot {
      display: block;
      grid-area: slot;
    }
    h1 {
      font-size: 2rem;
    }
    .stage .links {
      justify-self: center;
      margin: 0.75rem 0 0;
    }
  }
</style>

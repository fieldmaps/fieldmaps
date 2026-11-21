<script lang="ts" generics="S extends { title: string; text: string; layers: string[] }">
  import type * as maplibregl from "maplibre-gl";
  import type { Snippet } from "svelte";
  import ScrollHint from "./ScrollHint.svelte";
  import { stepKeys } from "./keys";
  import { createMap, reduced } from "./map/map";

  let {
    title,
    steps,
    options,
    move,
    intro,
    outro,
  }: {
    title: string;
    steps: S[];
    options: (container: HTMLDivElement) => Omit<maplibregl.MapOptions, "container">;
    move: (map: maplibregl.Map, step: S, animate: boolean) => void;
    intro?: Snippet;
    outro?: Snippet;
  } = $props();

  const FADE = { duration: 600, delay: 0 };
  const OPACITY: Record<string, string[]> = {
    fill: ["fill-opacity"],
    line: ["line-opacity"],
    symbol: ["text-opacity"],
    circle: ["circle-opacity", "circle-stroke-opacity"],
  };

  let container: HTMLDivElement;
  let articles: HTMLElement[] = $state([]);
  let active = $state(-1);

  $effect(() => {
    const { map, destroy } = createMap(
      { container, interactive: false, ...options(container) },
      (m) => move(m, steps[Math.max(active, 0)], false),
    );
    const show = (i: number, animate: boolean) => {
      // Before step 1, show the finished product at step 1's camera.
      const step = steps[Math.max(i, 0)];
      const layers = i < 0 ? steps[steps.length - 1].layers : step.layers;
      for (const layer of map.getStyle().layers) {
        if (layer.type === "background") continue;
        const on = layers.includes(layer.id) ? 1 : 0;
        for (const prop of OPACITY[layer.type]) {
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
      move(map, step, animate);
    };
    let ready = false;
    map.once("style.load", () => {
      ready = true;
      show(active, false);
    });
    const observer = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) active = articles.indexOf(e.target as HTMLElement);
          else if (e.target === articles[0] && e.boundingClientRect.top > e.rootBounds!.bottom)
            active = -1;
          else continue;
          if (ready) show(active, !reduced);
        }
      },
      { rootMargin: "-45% 0px -45% 0px" },
    );
    articles.forEach((a) => observer.observe(a));
    const removeKeys = stepKeys(articles, () => active, reduced);
    return () => {
      removeKeys();
      observer.disconnect();
      destroy();
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
      <h1>{title}</h1>
      {@render intro?.()}
    </div>
    {#each steps as step, i (step.title)}
      <article class="step" class:active={i === active} bind:this={articles[i]}>
        <h2>{step.title}</h2>
        <p>{step.text}</p>
        {#if i === steps.length - 1}
          {@render outro?.()}
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
  .steps :global(.button) {
    align-self: flex-start;
    margin-top: 1rem;
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

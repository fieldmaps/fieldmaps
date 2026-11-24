<script
  lang="ts"
  generics="S extends { title: string; text: string; caption?: string; layers: string[] }"
>
  import type * as maplibregl from "maplibre-gl";
  import { type Snippet, untrack } from "svelte";
  import ScrollHint from "./ScrollHint.svelte";
  import { stepKeys, stepper } from "./keys";
  import { createMap, FADE_MS, reduced } from "./map/map";

  let {
    title,
    tagline,
    steps,
    options,
    move,
    sideways,
    before,
    refresh,
    controls,
    intro,
    outro,
  }: {
    title: string;
    tagline?: string;
    steps: S[];
    options: (container: HTMLDivElement) => Omit<maplibregl.MapOptions, "container">;
    move: (map: maplibregl.Map, step: S, animate: boolean) => void;
    // Left and right arrow keys call this instead of stepping.
    sideways?: (d: -1 | 1) => void;
    before?: S;
    refresh?: unknown;
    controls?: Snippet;
    intro?: Snippet;
    outro?: Snippet;
  } = $props();

  const FADE = { duration: FADE_MS, delay: 0 };
  // `{gap:holes}` in step text renders "holes" bold in the --gap colour.
  const parts = (text: string) =>
    text
      .split(/\{(\w+):([^}]+)\}/)
      .map((part, i, all) =>
        i % 3 === 0 ? { text: part } : i % 3 === 1 ? undefined : { text: part, key: all[i - 1] },
      );
  const OPACITY: Record<string, string[]> = {
    fill: ["fill-opacity"],
    line: ["line-opacity"],
    symbol: ["text-opacity"],
    circle: ["circle-opacity"],
  };

  // The opening camera is `before` when given, else step 1's.
  const cameraStep = (i: number) => (i < 0 && before ? before : steps[Math.max(i, 0)]);

  let container: HTMLDivElement;
  let articles: HTMLElement[] = $state([]);
  let active = $state(-1);
  let reshow: ((animate: boolean) => void) | undefined;
  let go: ((d: -1 | 1) => boolean) | undefined = $state();
  let to: ((i: number) => boolean) | undefined = $state();
  let story: HTMLElement;
  // The clicked arrow is re-created in the next step, so focus follows it there.
  let refocus: { button: string; until: number } | undefined;

  $effect(() => {
    const { map, destroy } = createMap(
      { container, interactive: false, ...untrack(() => options(container)) },
      (m) => move(m, cameraStep(active), false),
    );
    const show = (i: number, animate: boolean) => {
      move(map, cameraStep(i), animate);
      // Before step 1, show the finished product at the opening camera.
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
    };
    let ready = false;
    map.once("style.load", () => {
      ready = true;
      show(active, false);
      reshow = (animate) => show(active, animate);
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
    const steppers = stepper(articles, () => active, reduced);
    go = steppers.go;
    to = steppers.to;
    const removeKeys = stepKeys(
      steppers.go,
      untrack(() => sideways),
    );
    return () => {
      reshow = undefined;
      removeKeys();
      observer.disconnect();
      destroy();
    };
  });

  $effect(() => {
    void active;
    if (!refocus || performance.now() > refocus.until) return;
    if (document.activeElement && document.activeElement !== document.body) return;
    const nav = story.querySelector(".arrows");
    const button =
      nav?.querySelector<HTMLButtonElement>(`[data-arrow="${refocus.button}"]:not(:disabled)`) ??
      nav?.querySelector<HTMLButtonElement>("button:not(:disabled)");
    button?.focus({ preventScroll: true });
  });

  const click = (button: string, run: () => void) => {
    refocus = { button, until: performance.now() + 2000 };
    run();
  };

  // Re-show the active step when the caller's data changes, such as the selected country.
  $effect(() => {
    void refresh;
    untrack(() => reshow?.(!reduced));
  });
</script>

{#snippet arrows()}
  <nav class="arrows" aria-label="Steps">
    <button
      type="button"
      aria-label="Previous step"
      data-arrow="previous"
      disabled={active < 0}
      onclick={() => click("previous", () => go?.(-1))}
    >
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
        <path d="M6 15l6-6 6 6" fill="none" stroke="currentColor" stroke-width="2" />
      </svg>
    </button>
    <button
      type="button"
      aria-label="Next step"
      data-arrow="next"
      disabled={active >= steps.length - 1}
      onclick={() => click("next", () => go?.(1))}
    >
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
        <path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2" />
      </svg>
    </button>
    {#if active === steps.length - 1}
      <button
        type="button"
        class="top"
        data-arrow="top"
        onclick={() => click("next", () => to?.(-1))}
      >
        Back to top
      </button>
    {/if}
  </nav>
{/snippet}

<ScrollHint />
<section class="story" data-snap bind:this={story}>
  <div class="globe">
    <div class="map" bind:this={container}></div>
  </div>
  <div class="steps">
    {#if controls}
      <div class="controls">{@render controls()}</div>
    {/if}
    <div class="intro">
      <h1>{title}</h1>
      {#if tagline}<p class="tagline">{tagline}</p>{/if}
      {@render intro?.()}
      {#if active < 0}{@render arrows()}{/if}
    </div>
    {#each steps as step, i (step.title)}
      <article class="step" class:active={i === active} bind:this={articles[i]}>
        <h2>{step.title}</h2>
        <p>
          {#each parts(step.text) as part, j (j)}
            {#if part?.key}<strong class="key" style:color="var(--{part.key})">
                {part.text}
              </strong>{:else if part}{part.text}{/if}
          {/each}
        </p>
        {#if step.caption}
          <p class="caption">{step.caption}</p>
        {/if}
        {#if i === steps.length - 1}
          {@render outro?.()}
        {/if}
        {#if i === active}{@render arrows()}{/if}
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
  .tagline {
    max-width: 22rem;
    margin: 0.5rem 0 0;
    font-size: 1.15rem;
    line-height: 1.45;
    color: var(--ink-soft);
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
  .step p.caption {
    margin-top: 0.75rem;
    font-size: 0.9rem;
    color: var(--ink);
  }
  .arrows {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
  }
  .arrows button {
    display: grid;
    place-items: center;
    width: 2.25rem;
    height: 2.25rem;
    padding: 0;
    border: 1px solid var(--ink);
    background: var(--white);
    color: var(--ink);
    cursor: pointer;
  }
  .arrows button.top {
    width: auto;
    padding: 0 0.75rem;
    font: inherit;
    font-size: 0.9rem;
  }
  .arrows button:hover:not(:disabled) {
    background: var(--paper-light);
  }
  .arrows button:focus-visible {
    outline: 2px solid var(--ink);
    outline-offset: 2px;
  }
  .arrows button:disabled {
    opacity: 0.35;
    cursor: default;
  }
  .controls {
    position: sticky;
    top: calc(var(--header-h) + 1rem);
    z-index: 2;
    width: fit-content;
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

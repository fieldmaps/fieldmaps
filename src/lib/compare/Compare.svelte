<script lang="ts">
  import { tileUrl } from "../map/style";
  import { unionBox, type AttributeRow } from "./attributes";
  import CompareMap from "./CompareMap.svelte";
  import ComparePanel from "./ComparePanel.svelte";
  import HitsPanel from "./HitsPanel.svelte";
  import { CompareState } from "./state.svelte";

  // The controls panel's right edge, and the width from which the camera pads past it.
  const PANEL_REM = 16.75;
  const SIDE_MIN_REM = 72;

  const compare = new CompareState();
  let rows = $state.raw<AttributeRow[]>([]);
  let rem = $state(16);
  let width = $state(0);
  const insetLeft = $derived(width >= SIDE_MIN_REM * rem ? PANEL_REM * rem : 0);

  $effect(() => {
    rem = parseFloat(getComputedStyle(document.documentElement).fontSize);
    fetch(tileUrl("site/compare/attributes/attributes.json"))
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data: AttributeRow[]) => (rows = data))
      .catch(() => (rows = []));
  });

  // Sources can share a code for different places, so frame only the shown sources' parts.
  function shownBox(row: AttributeRow): number[] | null {
    const ids =
      compare.view === "fade" ? [compare.pair.a, compare.pair.b] : [compare.pair[compare.view]];
    const boxes = (row.parts ?? [])
      .filter((p) => (ids as string[]).includes(p.layer))
      .map((p) => p.bbox);
    return boxes.length ? unionBox(boxes) : row.bbox;
  }

  // A map click narrows to the clicked feature only when its source splits the code.
  function pick(iso3: string, source: string, name: string) {
    const row = rows.find((r) => r.iso3 === iso3);
    if (!row) return;
    const own = (row.parts ?? []).filter((p) => p.layer === source);
    const part = own.length > 1 ? (own.find((p) => p.name === name) ?? null) : null;
    // A click inside the focused code keeps its picked part unless it lands on another one.
    if (!part && compare.focus?.iso3 === iso3) return;
    compare.focusOn(row.iso3, shownBox(row), part ? [part] : [], false);
  }
</script>

<div class="compare" bind:clientWidth={width} style:--inset-left="{insetLeft}px">
  <div class="map">
    <CompareMap {compare} {insetLeft} onpick={pick} />
    <ComparePanel {compare} />
    <HitsPanel {compare} />
    {#if compare.focus}
      <button
        type="button"
        class="chip"
        aria-label="Clear highlight"
        onclick={() => (compare.focus = null)}
      >
        {compare.focus.iso3} <span aria-hidden="true">×</span>
      </button>
    {/if}
  </div>
</div>

<style>
  .compare {
    position: relative;
    height: calc(100dvh - var(--header-h));
    overflow: hidden;
    --float-shadow: 0 1px 2px rgb(0 0 0 / 0.12), 0 4px 16px rgb(0 0 0 / 0.14);
  }
  .map {
    position: absolute;
    inset: 0;
    isolation: isolate;
  }
  .chip {
    position: absolute;
    left: calc(var(--inset-left) + (100% - var(--inset-left)) / 2);
    transform: translateX(-50%);
    z-index: 3;
    top: 0.75rem;
    padding: 0.25rem 0.75rem;
    border: 1px solid var(--paper);
    background: var(--white);
    box-shadow: var(--float-shadow);
    color: var(--ink);
    font: inherit;
    font-size: 0.85rem;
    font-weight: 600;
    white-space: nowrap;
    cursor: pointer;
  }
  .chip span {
    margin-left: 0.25rem;
    color: var(--ink-soft);
  }
</style>

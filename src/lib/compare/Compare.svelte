<script lang="ts">
  import { untrack } from "svelte";
  import { tileUrl } from "../map/style";
  import {
    itemTitle,
    mergeItems,
    unionBox,
    type AttributeRow,
    type GeometryList,
    type ItemRow,
  } from "./attributes";
  import CompareMap from "./CompareMap.svelte";
  import ComparePanel from "./ComparePanel.svelte";
  import GeometryTable from "./GeometryTable.svelte";
  import HitsPanel from "./HitsPanel.svelte";
  import { CompareState, SOURCES, type View } from "./state.svelte";

  const IDS = SOURCES.map((s) => s.id);
  // The sidebar's width, its gap to the edge, the controls panel's right edge, and the side-by-side breakpoint.
  const PANE_REM = 24;
  const GAP_REM = 0.75;
  const PANEL_REM = 16.75;
  const SIDE_MIN_REM = 72;

  const compare = new CompareState();
  let rows = $state.raw<AttributeRow[]>([]);
  let items = $state.raw<ItemRow[]>([]);
  const merged = $derived(mergeItems(items, compare.pair.a, compare.pair.b));
  // The map draws only the differences the sidebar lists.
  let list = $state<GeometryList>("land");
  const listItems = $derived(merged.filter((r) => r.list === list).flatMap((r) => r.items ?? []));
  let rem = $state(16);
  let width = $state(0);
  // Below this width the sidebar covers the map's lower half, so the camera pads the bottom instead.
  const side = $derived(width >= SIDE_MIN_REM * rem);
  let paneHeight = $state(0);
  const inset = $derived(side ? (PANE_REM + GAP_REM) * rem : 0);
  const insetLeft = $derived(side ? PANEL_REM * rem : 0);
  const insetBottom = $derived(side ? 0 : paneHeight + GAP_REM * rem);

  $effect(() => {
    rem = parseFloat(getComputedStyle(document.documentElement).fontSize);
    fetch(tileUrl("site/compare/attributes/attributes.json"))
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data: AttributeRow[]) => (rows = data))
      .catch(() => (rows = []));
    fetch(tileUrl("site/compare/differences/items.json"))
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data: ItemRow[]) => (items = data))
      .catch(() => (items = []));
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

  // A difference, or a code in Voronoi, shows in Fade; the view picked before returns once it clears.
  let viewBefore: View | null = null;
  function borrowView(next: View) {
    viewBefore ??= compare.view;
    compare.view = next;
  }
  $effect(() => {
    if (compare.item || compare.focus || !viewBefore) return;
    const back = viewBefore;
    viewBefore = null;
    untrack(() => (compare.view = back));
  });

  // A focused difference of the other kind clears when the list switches.
  $effect(() => {
    const kind = list;
    untrack(() => {
      const row = compare.item && merged.find((it) => it.item === compare.item!.ids[0]);
      if (row && row.list !== kind) compare.item = null;
    });
  });

  function focusItem(row: ItemRow, label: string) {
    borrowView("fade");
    compare.hits = [];
    compare.focusItem(row, label);
  }

  function pickItem(id: string | null) {
    const row = id ? merged.find((it) => it.items?.includes(id)) : null;
    if (!row || row.list !== list) {
      compare.item = null;
      return;
    }
    borrowView("fade");
    compare.focusItem(row, itemTitle(row, IDS), false);
  }
</script>

<div
  class="compare"
  bind:clientWidth={width}
  class:side
  style:--inset="{inset}px"
  style:--inset-left="{insetLeft}px"
  style:--inset-bottom="{insetBottom}px"
  style:--pane="{PANE_REM}rem"
  style:--gap="{GAP_REM}rem"
>
  <div class="map">
    <CompareMap
      {compare}
      {inset}
      {insetLeft}
      {insetBottom}
      {listItems}
      onpick={pick}
      onitempick={pickItem}
    />
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
    {:else if compare.item}
      <button
        type="button"
        class="chip"
        aria-label="Clear highlight"
        onclick={() => (compare.item = null)}
      >
        {compare.item.label} <span aria-hidden="true">×</span>
      </button>
    {/if}
  </div>
  <aside class="pane" aria-label="Differences" bind:offsetHeight={paneHeight}>
    <GeometryTable
      items={merged}
      item={compare.item}
      pair={compare.pair}
      bind:list
      onitem={focusItem}
    />
  </aside>
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
  .pane {
    position: absolute;
    z-index: 4;
    right: var(--gap);
    bottom: var(--gap);
    left: var(--gap);
    height: 50%;
    display: flex;
    flex-direction: column;
    background: var(--white);
    border: 1px solid var(--paper);
    box-shadow: var(--float-shadow);
  }
  .side .pane {
    top: var(--gap);
    bottom: auto;
    left: auto;
    width: var(--pane);
    height: auto;
    max-height: calc(100% - 2 * var(--gap));
  }
  .pane > :global(*) {
    flex: 1 1 auto;
    min-height: 0;
  }
  .chip {
    position: absolute;
    left: calc(var(--inset-left) + (100% - var(--inset) - var(--inset-left)) / 2);
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

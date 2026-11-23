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
  import AttributesTable from "./AttributesTable.svelte";
  import CompareMap from "./CompareMap.svelte";
  import ComparePanel from "./ComparePanel.svelte";
  import GeometryTable from "./GeometryTable.svelte";
  import HitsPanel from "./HitsPanel.svelte";
  import { CompareState, SOURCES, type View } from "./state.svelte";

  type Tab = "map" | "geometry" | "attributes";
  const TABS: { id: Tab; label: string }[] = [
    { id: "map", label: "Map" },
    { id: "geometry", label: "Geometry" },
    { id: "attributes", label: "Attributes" },
  ];
  const IDS = SOURCES.map((s) => s.id);
  // The table pane's width beside the map, which the map pads its camera by.
  const PANE_REM = 36;

  const compare = new CompareState();
  let tab = $state<Tab>("map");
  let rows = $state.raw<AttributeRow[]>([]);
  let failed = $state(false);
  let items = $state.raw<ItemRow[]>([]);
  const merged = $derived(mergeItems(items, compare.pair.a, compare.pair.b));
  // The map draws only the differences the Geometry pane lists, and both kinds otherwise.
  let list = $state<GeometryList>("land");
  const listItems = $derived(
    tab === "geometry" ? merged.filter((r) => r.list === list).flatMap((r) => r.items ?? []) : null,
  );
  let rem = $state(16);
  let width = $state(0);
  const inset = $derived(tab === "map" ? 0 : Math.min(PANE_REM * rem, width));

  $effect(() => {
    rem = parseFloat(getComputedStyle(document.documentElement).fontSize);
    fetch(tileUrl("site/compare/attributes/attributes.json"))
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data: AttributeRow[]) => (rows = data))
      .catch(() => (failed = true));
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

  function focusRow(row: AttributeRow) {
    if (compare.mode === "voronoi") borrowView("fade");
    compare.focusOn(row.iso3, shownBox(row), [], true);
  }

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
  style:--inset="{inset}px"
  style:--pane="{PANE_REM}rem"
  style:--shift={tab === "map" ? "100%" : `max(0px, 100% - ${PANE_REM}rem)`}
>
  <div class="map">
    <CompareMap
      {compare}
      {inset}
      mapTab={tab === "map"}
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
  <div class="pane" class:open={tab !== "map"} inert={tab === "map"}>
    <div class="slide">
      {#if tab === "geometry"}
        <GeometryTable
          items={merged}
          item={compare.item}
          pair={compare.pair}
          bind:list
          onitem={focusItem}
        />
      {:else}
        <AttributesTable
          {rows}
          {failed}
          focus={compare.focus}
          pair={compare.pair}
          onfocus={focusRow}
        />
      {/if}
    </div>
  </div>
  <nav class="tabs" aria-label="Views">
    {#each TABS as t (t.id)}
      <button
        type="button"
        aria-current={tab === t.id ? "page" : undefined}
        onclick={() => (tab = t.id)}
      >
        {t.label}
      </button>
    {/each}
  </nav>
</div>

<style>
  .compare {
    position: relative;
    height: calc(100dvh - var(--header-h));
    overflow: hidden;
  }
  .map {
    position: absolute;
    inset: 0;
    isolation: isolate;
  }
  /* The pane slides over the full-width map with a transform, so nothing re-lays out mid-slide. */
  .pane {
    position: absolute;
    inset: 0;
    background: var(--white);
    transform: translateX(var(--shift));
    transition: transform 300ms cubic-bezier(0.2, 0, 0, 1);
  }
  .pane.open {
    border-left: 1px solid var(--paper);
  }
  .slide {
    display: flex;
    width: min(var(--pane), 100%);
    height: 100%;
  }
  .slide > :global(*) {
    flex: 1;
    min-width: 0;
  }
  .tabs,
  .chip {
    position: absolute;
    left: calc((100% - var(--inset)) / 2);
    transform: translateX(-50%);
    transition: left 300ms cubic-bezier(0.2, 0, 0, 1);
    z-index: 3;
  }
  .tabs {
    top: 0.75rem;
    display: flex;
    border: 1px solid var(--ink);
    background: var(--white);
  }
  .tabs button {
    padding: 0.3rem 0.9rem;
    border: 0;
    background: none;
    color: var(--ink);
    font: inherit;
    font-size: 0.85rem;
    cursor: pointer;
  }
  .tabs button + button {
    border-left: 1px solid var(--ink);
  }
  .tabs button:hover:not([aria-current]) {
    background: var(--paper-light);
  }
  .tabs button[aria-current="page"] {
    background: var(--ink);
    color: var(--white);
  }
  .chip {
    top: 3rem;
    padding: 0.25rem 0.75rem;
    border: 1px solid var(--paper);
    background: var(--white);
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
  /* The pane covers the whole map here, so the tabs sit above it and the table makes room. */
  @media (max-width: 36rem) {
    .tabs {
      left: 50%;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .pane,
    .tabs,
    .chip {
      transition: none;
    }
  }
</style>

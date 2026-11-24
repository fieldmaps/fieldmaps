<script lang="ts">
  import { untrack } from "svelte";
  import { itemMatches, itemTitle, type GeometryList, type ItemRow } from "./attributes";
  import Segmented from "./Segmented.svelte";
  import { SOURCES, type ItemFocus, type Slot } from "./state.svelte";

  let {
    items,
    item,
    pair,
    list = $bindable("land"),
    onitem,
  }: {
    items: ItemRow[];
    item: ItemFocus | null;
    pair: Record<Slot, string>;
    list?: GeometryList;
    onitem: (row: ItemRow, label: string) => void;
  } = $props();

  const LISTS: { id: GeometryList; label: string; note: string }[] = [
    {
      id: "land",
      label: "Land",
      note: "The two sources put this land in different territories.",
    },
    {
      id: "islands",
      label: "Islands",
      note: "A draws these islands, and B's Voronoi puts them in a different territory where B also draws islands.",
    },
  ];
  const LABELS = Object.fromEntries(SOURCES.map((s) => [s.id, s.label]));
  const IDS = SOURCES.map((s) => s.id);

  let query = $state("");
  const ab = $derived([pair.a, pair.b]);
  const shown = $derived(
    items.filter(
      (it) => it.item === item?.ids[0] || (it.list === list && itemMatches(it, ab, query)),
    ),
  );
  // Differences grouped under A's code, or B's when A has none, codes in order.
  const groupCode = (it: ItemRow) =>
    ab.map((s) => String(it[`code_${s}`] ?? "")).find(Boolean) ?? "";
  const groups = $derived.by(() => {
    const out: Record<string, ItemRow[]> = {};
    for (const it of shown) (out[groupCode(it)] ??= []).push(it);
    return Object.entries(out).sort(([x], [y]) =>
      x.localeCompare(y, "en", { sensitivity: "base" }),
    );
  });

  // Scrolls once per item, only when its rows sit outside the area below the sticky header.
  let scroller = $state<HTMLElement>();
  const focused = $derived(item?.ids[0]);
  $effect(() => {
    if (!focused) return;
    const row = untrack(() => items.find((it) => it.item === focused));
    if (row?.list) list = row.list;
    requestAnimationFrame(() => {
      const el = scroller?.querySelector<HTMLElement>(`[data-item="${focused}"]`);
      if (!el || !scroller) return;
      const rows = [
        ...scroller.querySelectorAll<HTMLElement>(`[data-group="${el.dataset.group}"]`),
      ];
      const head = scroller.querySelector("thead")?.getBoundingClientRect().height ?? 0;
      const box = scroller.getBoundingClientRect();
      const top = rows[0].getBoundingClientRect().top - box.top - head;
      const bottom = rows.at(-1)!.getBoundingClientRect().bottom - box.top;
      if (top < 0 || bottom > scroller.clientHeight) scroller.scrollTop += top;
    });
  });

  const slotOf = (source: string): Slot => (source === pair.a ? "a" : "b");
  const label = (it: ItemRow) => itemTitle(it, IDS);
</script>

<div class="table-view">
  <div class="controls">
    <Segmented
      label="List"
      options={LISTS.map((l) => ({ id: l.id, label: l.label }))}
      current={list}
      pick={(id) => (list = id)}
    />
    <input type="search" placeholder="Search code or name" aria-label="Search" bind:value={query} />
    <span class="count">{shown.length} differences</span>
    <p class="note">{LISTS.find((l) => l.id === list)?.note}</p>
  </div>
  <div class="scroll" bind:this={scroller}>
    <table>
      <thead>
        <tr>
          <th class="code">ISO3</th>
          {#each ab as source (source)}
            <th>
              <span class="badge" style:--color="var(--compare-{slotOf(source)})">
                {slotOf(source).toUpperCase()}
              </span>
              {LABELS[source]}
            </th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each groups as [code, rows] (code)}
          {#each rows as it, i (it.item)}
            <tr
              class:start={i === 0}
              class:focused={it.item === item?.ids[0]}
              data-item={it.item}
              data-group={code}
              tabindex="0"
              onclick={() => onitem(it, label(it))}
              onkeydown={(e) => e.key === "Enter" && onitem(it, label(it))}
            >
              {#if i === 0}
                <th class="code" rowspan={rows.length}>{code}</th>
              {/if}
              {#each ab as source (source)}
                {@const itemCode = String(it[`code_${source}`] ?? "")}
                {@const name = it[`name_${source}`]}
                {@const absent = it.missing?.includes(source)}
                <td
                  class:empty={!name}
                  class:absent
                  title={absent ? "No territory of its own here" : undefined}
                >
                  {#if itemCode && itemCode !== code}
                    <span class="iso" style:color="var(--compare-{slotOf(source)})">
                      {itemCode}
                    </span>
                  {/if}
                  {name ?? ""}
                  {#if source === pair.a && it.type === "no_land"}
                    <div class="meta">No OSM land</div>
                  {/if}
                </td>
              {/each}
            </tr>
          {/each}
        {/each}
      </tbody>
    </table>
    {#if !shown.length}
      <p class="none">Nothing matches.</p>
    {/if}
  </div>
</div>

<style>
  .table-view {
    display: grid;
    grid-template-rows: auto 1fr;
    height: 100%;
    min-height: 0;
    font-size: 0.8125rem;
  }
  .controls {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--paper);
  }
  input[type="search"] {
    flex: 1 1 8rem;
    padding: 0.3rem 0.5rem;
    border: 1px solid var(--ink);
    font: inherit;
  }
  .count {
    margin-left: auto;
    color: var(--ink-soft);
  }
  .note {
    flex-basis: 100%;
    margin: 0;
    color: var(--ink-soft);
    font-size: 0.75rem;
  }
  .scroll {
    overflow: auto;
  }
  table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
  }
  th,
  td {
    min-width: 8rem;
    max-width: 16rem;
    padding: 0.25rem 0.5rem;
    text-align: left;
    vertical-align: top;
  }
  thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    border-bottom: 1px solid var(--ink);
    background: var(--white);
    font-weight: 600;
  }
  .code {
    position: sticky;
    left: 0;
    z-index: 2;
    min-width: 4rem;
    background: var(--white);
    font-weight: 600;
  }
  thead .code {
    z-index: 3;
  }
  tr.start > * {
    border-top: 1px solid var(--paper);
  }
  tbody tr {
    cursor: pointer;
  }
  tbody tr:hover > td,
  tr.focused > * {
    background: var(--paper-light);
  }
  .empty {
    background: var(--paper-light);
  }
  .absent {
    outline: 1px dashed var(--ink-soft);
    outline-offset: -3px;
  }
  .iso {
    margin-right: 0.35em;
    font-size: 0.75rem;
    font-weight: 600;
  }
  .meta {
    color: var(--ink-soft);
    font-size: 0.7rem;
  }
  .badge {
    display: inline-block;
    min-width: 1.25rem;
    margin-right: 0.25rem;
    color: var(--white);
    background: var(--color);
    font-size: 0.7rem;
    font-weight: 700;
    text-align: center;
  }
  .none {
    padding: 1rem;
    color: var(--ink-soft);
  }
</style>

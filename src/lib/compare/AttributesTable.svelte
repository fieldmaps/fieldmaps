<script lang="ts">
  import { attributeGroups, marked, matches, value, type AttributeRow } from "./attributes";
  import Segmented from "./Segmented.svelte";
  import { SOURCES, type Focus, type Slot } from "./state.svelte";

  let {
    rows,
    failed,
    focus,
    pair,
    onfocus,
  }: {
    rows: AttributeRow[];
    failed: boolean;
    focus: Focus | null;
    pair: Record<Slot, string>;
    onfocus: (row: AttributeRow) => void;
  } = $props();

  // One reference shows beside A and B, never compared: M49 where it has the attribute, else UNTERM.
  const REFS = ["m49", "unterm"];
  const LABELS: Record<string, string> = {
    ...Object.fromEntries(SOURCES.map((s) => [s.id, s.label])),
    m49: "M49",
    unterm: "UNTERM",
  };

  let picked = $state("name");
  let query = $state("");

  // The map pair is in charge: the table lists only codes where B differs from A.
  const ab = $derived([pair.a, pair.b]);
  const groups = $derived(
    attributeGroups(rows[0], Object.keys(LABELS)).filter((g) =>
      ab.every((s) => g.sources.includes(s)),
    ),
  );
  // The picked attribute falls back to the first when the pair lacks it.
  const group = $derived(groups.find((g) => g.key === picked) ?? groups[0]);
  const reference = $derived(REFS.find((s) => group?.sources.includes(s)));
  const columns = $derived(reference ? [...ab, reference] : ab);
  const shown = $derived(
    group
      ? rows.filter((row) => row.iso3 === focus?.iso3 || matches(row, group.key, ab, query))
      : [],
  );

  // Scrolls once per code, only when its row sits outside the area below the sticky header.
  // scrollIntoView would also scroll the hidden pane's ancestors.
  let scroller = $state<HTMLElement>();
  const focusedCode = $derived(focus?.iso3);
  $effect(() => {
    if (!focusedCode) return;
    requestAnimationFrame(() => {
      const row = scroller?.querySelector<HTMLElement>(`[data-iso3="${focusedCode}"]`);
      if (!row || !scroller) return;
      const head = scroller.querySelector("thead")?.getBoundingClientRect().height ?? 0;
      const box = scroller.getBoundingClientRect();
      const top = row.getBoundingClientRect().top - box.top - head;
      if (top < 0 || row.getBoundingClientRect().bottom - box.top > scroller.clientHeight)
        scroller.scrollTop += top;
    });
  });

  const slotOf = (source: string) => (["a", "b"] as const).find((k) => pair[k] === source);
</script>

<div class="table-view">
  <div class="controls">
    <input type="search" placeholder="Search code or name" aria-label="Search" bind:value={query} />
    {#if groups.length}
      <Segmented
        label="Attribute"
        options={groups.map((g) => ({ id: g.key, label: g.label }))}
        current={group.key}
        pick={(id) => (picked = id)}
      />
    {/if}
    <span class="count">{shown.length} of {rows.length} codes</span>
  </div>
  {#if failed}
    <p class="none">Could not load the attributes.</p>
  {:else}
    <div class="scroll" bind:this={scroller}>
      <table>
        <thead>
          <tr>
            <th class="code">ISO3</th>
            {#each columns as source (source)}
              {@const slot = slotOf(source)}
              <th>
                {#if slot}
                  <span class="badge" style:--color="var(--compare-{slot})">
                    {slot.toUpperCase()}
                  </span>
                {/if}
                {LABELS[source]}
              </th>
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each shown as row (row.iso3)}
            {@const diff = marked(row, group.key, ab, pair.a)}
            <tr class:focused={row.iso3 === focus?.iso3} data-iso3={row.iso3}>
              <th class="code">
                <button type="button" title="Show on map" onclick={() => onfocus(row)}>
                  {row.iso3}
                </button>
              </th>
              {#each columns as source (source)}
                {@const v = value(row, group.key, source)}
                <td class:empty={!v} class:diff={diff.has(source)} class:ref={source === reference}>
                  {v}
                </td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
      {#if rows.length && !shown.length}
        <p class="none">Nothing matches.</p>
      {/if}
    </div>
  {/if}
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
    border-top: 1px solid var(--paper);
    text-align: left;
    vertical-align: top;
  }
  thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    border-top: 0;
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
  }
  thead .code {
    z-index: 3;
  }
  .code button {
    padding: 0;
    border: 0;
    background: none;
    color: var(--link);
    font: inherit;
    font-weight: 600;
    text-decoration: underline;
    text-underline-offset: 2px;
    cursor: pointer;
  }
  tr.focused > * {
    background: var(--paper-light);
  }
  .empty {
    background: var(--paper-light);
  }
  .diff {
    background: color-mix(in srgb, var(--compare-b) 20%, var(--white));
  }
  .ref {
    color: var(--ink-soft);
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

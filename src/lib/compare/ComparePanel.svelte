<script lang="ts">
  import Segmented from "./Segmented.svelte";
  import { BASEMAPS, MODES, SLOTS, SOURCES, VIEWS, type CompareState } from "./state.svelte";

  let { compare }: { compare: CompareState } = $props();
</script>

<div class="panel">
  <h1 class="sr-only">Compare international boundaries</h1>
  <a class="back" href="/international/">
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6" /></svg>
    Overview
  </a>
  <h2>Basemap</h2>
  <Segmented
    label="Basemap"
    options={BASEMAPS}
    current={compare.basemap}
    pick={(id) => (compare.basemap = id)}
  />
  <h2>Geometry</h2>
  <Segmented
    label="Geometry"
    options={MODES}
    current={compare.mode}
    pick={(id) => (compare.mode = id)}
  />
  <h2>View</h2>
  <Segmented
    label="View"
    options={VIEWS}
    current={compare.view}
    pick={(id) => (compare.view = id)}
  />
  <h2>Compare</h2>
  <table>
    <thead>
      <tr>
        <th></th>
        {#each SLOTS as slot (slot)}
          <th>
            <span class="badge" style:--color="var(--compare-{slot})">{slot.toUpperCase()}</span>
          </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each SOURCES as s (s.id)}
        <tr>
          <td>{s.label}</td>
          {#each SLOTS as slot (slot)}
            <td>
              <input
                type="radio"
                name="source-{slot}"
                style:accent-color="var(--compare-{slot})"
                checked={compare.pair[slot] === s.id}
                onchange={() => compare.pick(slot, s.id)}
                aria-label="{slot.toUpperCase()}: {s.label}"
              />
            </td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>
  <p class="hint">Press [ or ] to switch views.</p>
</div>

<style>
  .panel {
    position: absolute;
    top: 0.75rem;
    left: 0.75rem;
    width: 16rem;
    padding: 0.75rem;
    background: var(--white);
    border: 1px solid var(--paper);
    font-size: 0.85rem;
  }
  .back {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--ink);
    font-weight: 600;
    text-decoration: none;
    margin-bottom: 0.75rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--paper);
  }
  .back:hover {
    text-decoration: underline;
  }
  .back svg {
    width: 1rem;
    height: 1rem;
    fill: none;
    stroke: currentColor;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  h2 {
    margin: 0.75rem 0 0.35rem;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--ink-soft);
  }
  h2:first-child {
    margin-top: 0;
  }
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip-path: inset(50%);
    white-space: nowrap;
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  td,
  th {
    padding: 0.15rem 0.25rem;
  }
  td:first-child {
    width: 100%;
  }
  td:not(:first-child),
  th {
    width: 1.75rem;
    text-align: center;
  }
  tbody tr:hover {
    background: var(--paper-light);
  }
  .badge {
    display: inline-block;
    min-width: 1.25rem;
    color: var(--white);
    background: var(--color);
    font-size: 0.7rem;
    font-weight: 700;
  }
  .hint {
    margin: 0.75rem 0 0;
    color: var(--ink-soft);
    font-size: 0.75rem;
  }
</style>

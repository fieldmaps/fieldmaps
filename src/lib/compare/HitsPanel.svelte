<script lang="ts">
  import type { CompareState } from "./state.svelte";

  let { compare }: { compare: CompareState } = $props();
</script>

{#if compare.hits.length}
  <div class="hits">
    <header>
      <h2>At this point</h2>
      <button type="button" aria-label="Close" onclick={() => (compare.hits = [])}>×</button>
    </header>
    {#each compare.hits as hit, i (i)}
      <section>
        <h3>
          <span class="badge" style:--color="var(--compare-{hit.slot})">
            {hit.slot.toUpperCase()}
          </span>
          {hit.label}
        </h3>
        <table>
          <tbody>
            {#each Object.entries(hit.properties) as [key, value] (key)}
              <tr><th>{key}</th><td>{value ?? ""}</td></tr>
            {/each}
          </tbody>
        </table>
      </section>
    {/each}
  </div>
{/if}

<style>
  .hits {
    position: absolute;
    z-index: 3;
    top: 0.75rem;
    right: 0.75rem;
    width: 20rem;
    max-height: calc(100% - 1.5rem);
    overflow-y: auto;
    padding: 0.75rem;
    background: var(--white);
    border: 1px solid var(--paper);
    font-size: 0.85rem;
  }
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  h2 {
    margin: 0;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--ink-soft);
  }
  button {
    border: 0;
    background: none;
    font-size: 1.25rem;
    line-height: 1;
    color: var(--ink-soft);
    cursor: pointer;
  }
  section + section {
    border-top: 1px solid var(--paper);
  }
  h3 {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin: 0.6rem 0 0.3rem;
    font-size: 0.85rem;
  }
  .badge {
    min-width: 1.25rem;
    text-align: center;
    color: var(--white);
    background: var(--color);
    font-size: 0.7rem;
    font-weight: 700;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.75rem;
    line-height: 1.4;
    margin-bottom: 0.5rem;
  }
  th,
  td {
    padding: 0.1rem 0.75rem 0.1rem 0;
    text-align: left;
    vertical-align: top;
    overflow-wrap: anywhere;
  }
  th {
    width: 40%;
    font-weight: 400;
    color: var(--ink-soft);
  }
  td {
    font-family: var(--font-mono);
  }
</style>

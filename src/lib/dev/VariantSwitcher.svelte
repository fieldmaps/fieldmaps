<script lang="ts">
  // Dev-only picker for layout variants under review; the pick is mirrored to ?variant-<name>=.
  let {
    name,
    options,
    value = $bindable(),
  }: { name: string; options: string[]; value: string } = $props();

  const key = `variant-${name}`;
  const linked = new URLSearchParams(location.search).get(key);
  if (linked && options.includes(linked)) value = linked;

  function pick(option: string) {
    value = option;
    const url = new URL(location.href);
    url.searchParams.set(key, option);
    history.replaceState(history.state, "", url);
  }
</script>

<div class="variants" role="radiogroup" aria-label="{name} variant">
  <span>{name}</span>
  {#each options as option (option)}
    <button type="button" role="radio" aria-checked={value === option} onclick={() => pick(option)}>
      {option}
    </button>
  {/each}
</div>

<style>
  .variants {
    position: fixed;
    left: 0.75rem;
    bottom: 0.75rem;
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem;
    background: #fff8c5;
    border: 2px dashed #b08800;
    font:
      600 0.75rem/1 system-ui,
      sans-serif;
    color: #3d2e00;
  }
  span {
    padding: 0 0.35rem;
  }
  button {
    padding: 0.3rem 0.55rem;
    border: 1px solid #b08800;
    background: #ffffff;
    color: inherit;
    font: inherit;
    cursor: pointer;
  }
  button[aria-checked="true"] {
    background: #3d2e00;
    color: #ffffff;
  }
</style>

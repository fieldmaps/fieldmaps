<script lang="ts" generics="T extends string | number">
  let {
    label,
    options,
    current,
    pick,
  }: { label: string; options: { id: T; label: string }[]; current: T; pick: (id: T) => void } =
    $props();
</script>

<div class="segmented" role="radiogroup" aria-label={label}>
  {#each options as o (o.id)}
    <label>
      <input type="radio" name={label} checked={current === o.id} onchange={() => pick(o.id)} />
      {o.label}
    </label>
  {/each}
</div>

<style>
  .segmented {
    display: flex;
    border: 1px solid var(--ink);
  }
  label {
    flex: 1 1 0;
    text-align: center;
    padding: 0.3rem 0.6rem;
    border-left: 1px solid var(--ink);
    background: var(--white);
    color: var(--ink);
    cursor: pointer;
  }
  label:first-child {
    border-left: 0;
  }
  label:hover:not(:has(:checked)) {
    background: var(--paper-light);
  }
  label:has(:checked) {
    background: var(--ink);
    color: var(--white);
  }
  label:has(:focus-visible) {
    outline: 2px solid var(--ink);
    outline-offset: 2px;
  }
  input {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip-path: inset(50%);
    white-space: nowrap;
  }
</style>

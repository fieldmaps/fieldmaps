<script lang="ts">
  import { CompareState } from "./state.svelte";
  import CompareMap from "./CompareMap.svelte";
  import ComparePanel from "./ComparePanel.svelte";
  import HitsPanel from "./HitsPanel.svelte";

  const compare = new CompareState();
</script>

<div class="compare">
  <CompareMap {compare} />
  <ComparePanel {compare} />
  <HitsPanel {compare} />
</div>

<style>
  .compare {
    position: relative;
    height: calc(100dvh - var(--header-h));
  }
</style>

<script lang="ts">
  interface Props {
    children?: import('svelte').Snippet;
  }

  let { children }: Props = $props();
</script>

<svelte:head>
  <title>Data | Fieldmaps.io</title>
</svelte:head>

{@render children?.()}

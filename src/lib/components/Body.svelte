<script lang="ts">
  interface Props {
    children?: import('svelte').Snippet;
  }

  let { children }: Props = $props();
</script>

<section class="section">
  <div class="container is-max-widescreen">
    <div class="content">
      {@render children?.()}
    </div>
  </div>
</section>

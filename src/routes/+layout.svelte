<script lang="ts">
  import 'bulma/css/bulma.css';
  interface Props {
    children?: import('svelte').Snippet;
  }

  let { children }: Props = $props();

  const url = 'https://fieldmaps.io/';
  const img = 'https://fieldmaps.io/img/edge-matched-preview.png';
  const title = 'FieldMaps — Humanitarian Maps & Data';
  const description =
    'Mobile, offline, interactive reference maps & globally aggregated datasets for humanitarian use.';
</script>

<svelte:head>
  <meta name="title" content={title} />
  <meta name="description" content={description} />
  <meta property="og:type" content="website" />
  <meta property="og:url" content={url} />
  <meta property="og:title" content={title} />
  <meta property="og:description" content={description} />
  <meta property="og:image" content={img} />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:url" content={url} />
  <meta name="twitter:title" content={title} />
  <meta name="twitter:description" content={description} />
  <meta name="twitter:image" content={img} />
</svelte:head>

{@render children?.()}

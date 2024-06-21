<script lang="ts">
  import Body from '$lib/components/Body.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Header from '$lib/components/Header.svelte';
</script>

<svelte:head>
  <title>Maps | Fieldmaps.io</title>
</svelte:head>
<Header active="maps" />
<Body>
  <h1 class="has-text-centered">Atlas Maps</h1>
  <p class="has-text-centered">
    <a href="https://atlas.fieldmaps.io/">
      <img src="/img/atlas.png" alt="atlas" />
    </a>
  </p>
  <p>
    Currently, a map style based on global edge-matched subnational boundaries is being developed. A
    preview of this style is available here: <a href="https://atlas.fieldmaps.io/"
      >atlas.fieldmaps.io</a
    >.
  </p>
  <p>
    Development priority is currently towards global map styles, however country-specific layers
    remain available at URLs like the following: <a href="https://atlas.fieldmaps.io/ssd"
      >atlas.fieldmaps.io/ssd</a
    >.
  </p>
</Body>
<Footer />

<script lang="ts">
  import Body from '$lib/components/Body.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Header from '$lib/components/Header.svelte';
  import HeaderData from '$lib/components/HeaderData.svelte';
  import TableSrc from '$lib/components/TableSrc.svelte';
  import { geoboundaries } from '$lib/stores';

  const dataUrl = 'https://data.fieldmaps.io/geoboundaries';
</script>

<Header active="data" />
<HeaderData active="geoboundaries" />
<Body>
  <h1 class="has-text-centered">geoBoundaries</h1>
  <p class="has-text-centered">
    <img src="/img/geoboundaries.png" alt="cod" />
  </p>
  <p>
    Visit <a href="https://www.geoboundaries.org/">geoboundaries.org</a> for the latest information about
    geoBoundaries layers. Data below is automatically downloaded from the geoBoundaries API at the source
    URLs below before processed for edge matching. Extended layers can be downloaded and clipped to any
    ADM0, with the original layer available for reference.
  </p>
  <TableSrc data={$geoboundaries} />
  <p>
    Download metadata table as: <a href={dataUrl + '.json'}>json</a> |
    <a href={dataUrl + '.csv'}>csv</a> |
    <a href={dataUrl + '.xlsx'}>xlsx</a>
  </p>
</Body>
<Footer />

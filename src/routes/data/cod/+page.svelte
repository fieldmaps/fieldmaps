<script lang="ts">
  import Body from '$lib/components/Body.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Header from '$lib/components/Header.svelte';
  import HeaderData from '$lib/components/HeaderData.svelte';
  import TableSrc from '$lib/components/TableSrc.svelte';
  import { cod } from '$lib/stores';

  const dataUrl = 'https://data.fieldmaps.io/cod';
  const pcodeUrl = 'https://data.fieldmaps.io/global-pcodes';
</script>

<Header active="data" />
<HeaderData active="cod" />
<Body>
  <h1 class="has-text-centered">Common Operational Datasets</h1>
  <p class="has-text-centered">
    <img src="/img/cod.png" alt="cod" />
  </p>
  <p>
    Visit <a href="https://cod.unocha.org/">cod.unocha.org</a> for the latest information about OCHA
    COD layers. Data below is automatically extracted from the
    <a href="https://codgis.itos.uga.edu/arcgis/rest/services/">ITOS ArcGIS Server</a> before processed
    for edge matching. Extended layers can be downloaded and clipped to any ADM0, with the original layer
    available for reference.
  </p>
  <p>
    To obtain a list of global P-Codes used in global edge-matched subnational boundaries:
    <a href={pcodeUrl + '.json'}>json</a> |
    <a href={pcodeUrl + '.csv'}>csv</a> |
    <a href={pcodeUrl + '.xlsx'}>xlsx</a>
  </p>
  <TableSrc data={$cod} />
  <p>
    Download metadata table as:
    <a href={dataUrl + '.json'}>json</a> |
    <a href={dataUrl + '.csv'}>csv</a> |
    <a href={dataUrl + '.xlsx'}>xlsx</a>
  </p>
</Body>
<Footer />

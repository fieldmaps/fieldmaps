<script lang="ts">
  import Body from '$lib/components/Body.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Header from '$lib/components/Header.svelte';
  import HeaderData from '$lib/components/HeaderData.svelte';
  import TablePop from '$lib/components/TablePop.svelte';
  import { getJSON } from '$lib/utils';
  import { onMount } from 'svelte';

  const dataUrl = 'https://data.fieldmaps.io/population';
  const options = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  };

  let data = $state([]);

  onMount(async () => {
    data = await getJSON('population');
  });
</script>

<Header active="data" />
<HeaderData active="population" />
<Body>
  <h1 class="has-text-centered">Global Subnational Population</h1>
  <p class="has-text-centered">
    <img src="/img/population.png" alt="population" />
  </p>
  <p>
    Updated: {data[0] ? new Date(data[0].date).toLocaleDateString('en-GB', options) : ''}
  </p>
  <p>
    Population statistics using data from
    <a href="https://www.worldpop.org/geodata/listing?id=29"
      >WorldPop Unconstrained Individual Countries
    </a>
    to create a complete global coverage population raster. Results are aggregated to
    <a href="https://data.fieldmaps.io/edge-matched/humanitarian/intl/adm4_polygons.gpkg.zip"
      >humanitarian edge-matched boundaries</a
    >, adjusted so that ADM0 totals match those of the 2024 projections in the
    <a href="https://population.un.org/wpp/Download/Standard/CSV/"
      >United Nations World Population Prospects</a
    >.
  </p>
  <TablePop {data} />
  <p>
    <b>Attribution</b>: FieldMaps, United Nations, WorldPop
  </p>
  <p>
    <b>License</b>:
    <a href="https://creativecommons.org/licenses/by/4.0/">
      Creative Commons Attribution 4.0 International
    </a>
    (CC BY 4.0)
  </p>
  <p>
    <b>Conditions</b>: Derived work must include attributions
  </p>
  <br /><br /><br />
  <p>
    Download metadata tables as: <a href={dataUrl + '.json'}>json</a> |
    <a href={dataUrl + '.csv'}>csv</a> |
    <a href={dataUrl + '.xlsx'}>xlsx</a>
  </p>
</Body>
<Footer />

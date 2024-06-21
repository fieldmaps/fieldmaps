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

  let data = [];

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
    <!-- <a href="https://cod.unocha.org/">OCHA / UNFPA Common Operational Datasets</a>, -->
    <a href="https://dataforgood.facebook.com/dfg/tools/high-resolution-population-density-maps">
      Meta/Facebook High Resolution Population Density Maps
    </a>
    and
    <a href="https://www.worldpop.org/geodata/listing?id=29"
      >WorldPop Unconstrained Individual Countries
    </a>
    to create a complete global coverage population raster. Results are aggregated to
    <a href="https://data.fieldmaps.io/edge-matched/humanitarian/intl/adm4_polygons.gpkg.zip"
      >humanitarian edge-matched boundaries</a
    >, adjusted so that ADM0 totals match those of the 2022 projections in the
    <a href="https://population.un.org/wpp/Download/Standard/CSV/"
      >United Nations World Population Prospects</a
    >. The following population datasets are available for download:
  </p>
  <ul>
    <!-- <li>
      <b>Common Operational Datasets</b>: Default version recommended for use. Mixed source data
      including OCHA / UNFPA sex and age disaggregated data (SADD), filling gaps with Meta /
      Facebook and WorldPop.
    </li> -->
    <li>
      <b>Meta / Facebook</b>: Data from Meta / Facebook, filling gaps with WorldPop. Contains
      limited sex and age groups.
    </li>
    <li>
      <b>WorldPop</b>: Data only from WorldPop. Contains no sex or age groups, only totals.
    </li>
  </ul>
  <TablePop {data} />
  <p>
    <b>Attribution</b>: FieldMaps, United Nations,
    <!-- OCHA, UNFPA,  -->
    Meta / Facebook, WorldPop
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

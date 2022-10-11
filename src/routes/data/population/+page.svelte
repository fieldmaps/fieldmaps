<script lang="ts">
  import Header from '$lib/Header.svelte';
  import HeaderData from '$lib/HeaderData.svelte';
  import Body from '$lib/Body.svelte';
  import TablePop from '$lib/TablePop.svelte';
  import Footer from '$lib/Footer.svelte';
  import data from '../../../data/population.json';

  const dataUrl = 'https://data.fieldmaps.io/population';
  const options = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  };
</script>

<Header active="data" />
<HeaderData active="population" />
<Body>
  <h1 class="has-text-centered">Global Subnational Population</h1>
  <p class="has-text-centered">
    <img src="/img/population.png" alt="population" />
  </p>
  <p>Updated: {new Date(data[0]?.date).toLocaleDateString('en-GB', options)}</p>
  <p>
    Population statistics using <a
      href="https://dataforgood.facebook.com/dfg/tools/high-resolution-population-density-maps"
    >
      Meta/Facebook High Resolution Population Density Maps
    </a>
    where available, filling in gaps with
    <a href="https://www.worldpop.org/geodata/listing?id=29">
      WorldPop Unconstrained Individual Countries
    </a>
    to create a complete global coverage population raster. Results are aggregated
    to
    <a
      href="https://data.fieldmaps.io/edge-matched/humanitarian/intl/adm4_polygons.gpkg.zip"
      >humanitarian edge-matched boundaries</a
    >, adjusted so that ADM0 totals match those of the 2022 projections in the
    <a href="https://population.un.org/wpp/Download/Standard/CSV/"
      >United Nations World Population Prospects</a
    >. The following population datasets are available for download:
  </p>
  <ul>
    <li>
      <b>UN WPP</b>: Mixed source data including Meta / Facebook where
      available, falling back to WorldPop. Default version recommended for use.
    </li>
    <li>
      <b>Meta / Facebook</b>: Contains data only from Meta / Facebook with
      partial global coverage.
    </li>
    <li>
      <b>WorldPop</b>: Contains data only from WorldPop with full global
      coverage.
    </li>
  </ul>
  <TablePop {data} />
  <p>
    <b>Attribution</b>: FieldMaps, United Nations, Meta / Facebook, WorldPop
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
  <p>The following population attributes are present in the data:</p>
  <div class="table-container">
    <table class="table">
      <thead><tr><th>Attribute</th><th>Description</th> </tr> </thead>
      <tbody>
        <tr><td>t</td><td>general population</td></tr>
        <tr><td>f</td> <td>women</td></tr>
        <tr><td>m</td><td>men</td></tr>
        <tr><td>t_00_04</td><td>children under five</td></tr>
        <tr><td>t_15_24</td><td>youth (15-24)</td></tr>
        <tr><td>t_60_plus</td><td>elderly (60+)</td></tr>
        <tr><td>f_15_49</td><td>women of reproductive age (15-49)</td></tr>
      </tbody>
    </table>
  </div>
  <br /><br /><br />
  <p>
    Download metadata tables as: <a href={dataUrl + '.json'}>json</a> |
    <a href={dataUrl + '.csv'}>csv</a> |
    <a href={dataUrl + '.xlsx'}>xlsx</a>
  </p>
</Body>
<Footer />

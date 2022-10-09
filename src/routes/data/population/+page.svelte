<script lang="ts">
  import Header from '$lib/Header.svelte';
  import HeaderData from '$lib/HeaderData.svelte';
  import Body from '$lib/Body.svelte';
  import Footer from '$lib/Footer.svelte';
  import data from '../../../data/adm0.json';

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
  <h2>UN World Population Prospects, {new Date().getFullYear()} Projection</h2>
  <p>
    <a href="https://data.fieldmaps.io/population/un_wpp.xlsx">
      <b>Download data (xlsx)</b>
    </a>
  </p>
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
    >. See
    <a href="https://github.com/fieldmaps/population-statistics">GitHub</a> for technical
    information on how this layer is made.
  </p>
  <p>
    This population dataset is intended to be joined with edge-matched
    boundaries created on the same date, joining by admin ID. The following
    population attributes are present:
  </p>
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
  <p>
    Separate population datasets containing only a single source are also
    available for download. Conversion factors are also available, used for
    adjusting source totals to match UN World Population Prospects, {new Date().getFullYear()}
    Projection.
  </p>
  <div class="table-container">
    <table class="table">
      <thead>
        <tr>
          <th>Source</th> <th>Population Data</th> <th>Conversion Factors</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Meta/Facebook</td>
          <td>
            <a href="https://data.fieldmaps.io/population/meta_fb.xlsx">
              xlsx
            </a>
          </td>
          <td>
            <a href="https://data.fieldmaps.io/population/meta_fb_factor.json">
              json
            </a>
            |
            <a href="https://data.fieldmaps.io/population/meta_fb_factor.csv">
              csv
            </a>
            |
            <a href="https://data.fieldmaps.io/population/meta_fb_factor.xlsx">
              xlsx
            </a>
          </td>
        </tr>
        <tr>
          <td>WorldPop</td>
          <td>
            <a href="https://data.fieldmaps.io/population/worldpop.xlsx">
              xlsx
            </a>
          </td>
          <td>
            <a href="https://data.fieldmaps.io/population/worldpop_factor.json">
              json
            </a>
            |
            <a href="https://data.fieldmaps.io/population/worldpop_factor.csv">
              csv
            </a>
            |
            <a href="https://data.fieldmaps.io/population/worldpop_factor.xlsx">
              xlsx
            </a>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</Body>
<Footer />

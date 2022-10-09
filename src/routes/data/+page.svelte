<script lang="ts">
  import Header from '$lib/Header.svelte';
  import HeaderData from '$lib/HeaderData.svelte';
  import Body from '$lib/Body.svelte';
  import Footer from '$lib/Footer.svelte';
  import TableDest from '$lib/TableDest.svelte';
  import data from '../../data/edge-matched.json';

  const dataUrl = 'https://data.fieldmaps.io/edge-matched';
  const options = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  };
</script>

<Header active="data" />
<HeaderData active="" />
<Body>
  <h1 class="has-text-centered">Global Edge-matched Subnational Boundaries</h1>
  <p class="has-text-centered">
    <img src="/img/edge-matched.png" alt="edge-matched" />
  </p>
  <p>
    Updated: {new Date(data[0].date).toLocaleDateString('en-GB', options)}
  </p>
  <h2>Humanitarian</h2>
  <p>
    Uses OCHA Common Operational Datasets (COD) when available, falling back to
    geoBoundaries for regions without coverage. Represents the latest available
    data for humanitarian operational use. Uses the OpenStreetMap International
    ADM0 worldview for edge-matching.
  </p>
  <TableDest data={data.filter((x) => x.grp === 'humanitarian')} />
  <p>
    <b>Attribution</b>: FieldMaps, OCHA, geoBoundaries, U.S. Department of
    State, OpenStreetMap
  </p>
  <p>
    <b>License</b>:
    <a href="https://opendatacommons.org/licenses/odbl/">
      Open Data Commons Open Database License
    </a>
    (ODbL)
  </p>
  <p>
    <b>Conditions</b>: Derived work must include attributions, be offered under
    the same license, and keep open access to the data
  </p>
  <h2>Open</h2>
  <p>
    Uses geoBoundaries exclusively to ensure all data comes from sources with
    clearly defined licenses. Suitable for academic or commercial use. Uses the
    U.S. Geological Survey International ADM0 worldview for edge-matching.
  </p>
  <TableDest data={data.filter((x) => x.grp === 'open')} />
  <p>
    <b>Attribution</b>: FieldMaps, geoBoundaries, U.S. Department of State, U.S.
    Geological Survey
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
  See
  <a href="https://github.com/fieldmaps/edge-extender">GitHub</a> for technical information
  on how edge-matching is performed.
</Body>
<Footer />

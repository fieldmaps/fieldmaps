<script lang="ts">
  import Body from '$lib/components/Body.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Header from '$lib/components/Header.svelte';
  import HeaderData from '$lib/components/HeaderData.svelte';
  import TableDest from '$lib/components/TableDest.svelte';
  import { getJSON } from '$lib/utils';
  import { onMount } from 'svelte';

  const dataUrl = 'https://data.fieldmaps.io/edge-matched';
  const options = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  };

  let data = $state([]);

  onMount(async () => {
    data = await getJSON('edge-matched');
  });
</script>

<Header active="data" />
<HeaderData active="" />
<Body>
  <h1 class="has-text-centered">Global Edge-matched Subnational Boundaries</h1>
  <p class="has-text-centered">
    <img src="/img/edge-matched.png" alt="edge-matched" />
  </p>
  <p>
    Updated: {data[0] ? new Date(data[0].date).toLocaleDateString('en-GB', options) : ''}
  </p>
  <h2>Humanitarian</h2>
  <p>
    Uses UN Common Operational Datasets (COD) when available, falling back to geoBoundaries for
    regions without coverage. Represents the latest available data for humanitarian operational use.
    Uses the OpenStreetMap International ADM0 worldview for edge-matching.
  </p>
  <TableDest data={data.filter((x) => x.grp === 'humanitarian')} />
  <p>
    <b>Attribution</b>: FieldMaps, UN CODs, geoBoundaries, U.S. Department of State, OpenStreetMap
  </p>
  <p>
    <b>License</b>:
    <a href="https://opendatacommons.org/licenses/odbl/">
      Open Data Commons Open Database License
    </a>
    (ODbL)
  </p>
  <p>
    <b>Conditions</b>: Derived work must include attributions, be offered under the same license,
    and keep open access to the data
  </p>
  <h2>Open</h2>
  <p>
    Uses geoBoundaries exclusively to ensure all data comes from sources with clearly defined
    licenses. Suitable for academic or commercial use. Uses the OpenStreetMap International ADM0
    worldview for edge-matching.
  </p>
  <TableDest data={data.filter((x) => x.grp === 'open')} />
  <p>
    <b>Attribution</b>: FieldMaps, geoBoundaries, U.S. Department of State, OpenStreetMap
  </p>
  <p>
    <b>License</b>:
    <a href="https://opendatacommons.org/licenses/odbl/">
      Open Data Commons Open Database License
    </a>
    (ODbL)
  </p>
  <p>
    <b>Conditions</b>: Derived work must include attributions, be offered under the same license,
    and keep open access to the data
  </p>
  <br /><br /><br />
  <p>
    Download metadata tables as: <a href={dataUrl + '.json'}>json</a> |
    <a href={dataUrl + '.csv'}>csv</a> |
    <a href={dataUrl + '.xlsx'}>xlsx</a>
  </p>
  See
  <a href="https://github.com/fieldmaps/edge-extender">GitHub</a> for technical information on how edge-matching
  is performed.
</Body>
<Footer />

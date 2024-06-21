<script lang="ts">
  import Body from '$lib/components/Body.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Header from '$lib/components/Header.svelte';
  import HeaderData from '$lib/components/HeaderData.svelte';
  import TableDest from '$lib/components/TableDest.svelte';
  import { getJSON } from '$lib/utils';
  import { onMount } from 'svelte';

  const dataUrl = 'https://data.fieldmaps.io/adm0';
  const options = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  };

  let data = [];

  onMount(async () => {
    data = await getJSON('adm0');
  });
</script>

<Header active="data" />
<HeaderData active="adm0" />
<Body>
  <h1 class="has-text-centered">Global International Boundaries</h1>
  <p class="has-text-centered">
    <img src="/img/adm0.png" alt="adm0" />
  </p>
  <p>
    Updated: {data[0] ? new Date(data[0].date).toLocaleDateString('en-GB', options) : ''}
  </p>
  <p>
    Very high resolution boundaries combining coastline data with
    <a href="https://hiu.state.gov/data/">
      U.S. Department of State Large Scale International Boundaries (LSIB)
    </a>
    for international boundaries and
    <a href="https://unstats.un.org/unsd/methodology/m49/overview/">
      United Nations Statistics Division M49
    </a>
    for attributes. See
    <a href="https://github.com/fieldmaps/adm0-generator">GitHub</a> for technical information on how
    this layer is made.
  </p>
  <p>
    International boundaries are built using either OpenStreetMap or U.S. Geological Survey
    coastlines. Within each set, ADM0 layers comes in several versions to represent different world
    views of disputed areas. Starting with the "All" version, areas are dissolved together based on
    varying international recognition. The following preset world views are available for download:
  </p>
  <ul>
    <li>
      <b>International</b>: A balanced world view for use by international non-governmental
      organizations. Disputed areas follow recommended representation used by the
      <a href="https://geoservices.un.org/Html5Viewer/index.html?viewer=clearmap">UN Clear Map</a>.
      UN agencies should use official layers at the
      <a href="https://geoservices.un.org/webapps/geohub/">UN Geospatial Hub</a>.
    </li>
    <li>
      <b>All</b>: A conservative world view that dissagregates all disputed areas. Useful if
      applying individual customization outside the presets generated here.
    </li>
  </ul>
  <h2>OpenStreetMap (ODbL)</h2>
  <p>
    Default version, uses <a href="https://osmdata.openstreetmap.de/data/land-polygons.html">
      OpenStreetMap
    </a>
    (<a href="https://osmdata.openstreetmap.de/download/land-polygons-complete-4326.zip">download</a
    >) for coastlines so that it aligns with web maps using OSM for basemaps or other data.
  </p>
  <TableDest adm0 data={data.filter((x) => x.grp === 'osm')} />
  <p>
    <b>Attribution</b>: FieldMaps, U.S. Department of State, OpenStreetMap
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
  <h2>U.S. Geological Survey (Public Domain)</h2>
  <p>
    Specialty version, uses <a href="https://rmgsc.cr.usgs.gov/gie/">U.S. Geological Survey</a>
    (<a
      href="https://rmgsc.cr.usgs.gov/outgoing/ecosystems/Global/USGSEsriWCMC_GlobalIslands_v3.mpk"
      >download</a
    >) for coastlines so that intellectual property and related rights in this dataset are absent.
  </p>
  <TableDest adm0 data={data.filter((x) => x.grp === 'usgs')} />
  <p>
    <b>Attribution</b>: FieldMaps, U.S. Department of State, U.S. Geological Survey
  </p>
  <p>
    <b>License</b>: Public Domain
  </p>
  <p>
    <b>Conditions</b>: None
  </p>
  <br /><br /><br />
  <p>
    Download metadata tables as: <a href={dataUrl + '.json'}>json</a> |
    <a href={dataUrl + '.csv'}>csv</a> |
    <a href={dataUrl + '.xlsx'}>xlsx</a>
  </p>
</Body>
<Footer />

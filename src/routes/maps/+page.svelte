<script lang="ts">
  import Body from '$lib/Body.svelte';
  import Footer from '$lib/Footer.svelte';
  import Header from '$lib/Header.svelte';

  const countries = [
    ['Afghanistan', 'afg'],
    ['Burundi', 'bdi'],
    ['Burkina Faso', 'bfa'],
    ['Central African Republic', 'caf'],
    ["Côte d'Ivoire", 'civ'],
    ['Cameroon', 'cmr'],
    ['Democratic Republic of the Congo', 'cod'],
    ['Columbia', 'col'],
    ['Eritrea', 'eri'],
    ['Ethiopia', 'eth'],
    ['Haiti', 'hti'],
    ['Iraq', 'irq'],
    ['Lebanon', 'lbn'],
    ['Lybia', 'lby'],
    ['Mali', 'mli'],
    ['Myanmar', 'mmr'],
    ['Mozambique', 'moz'],
    ['Niger', 'ner'],
    ['Nigeria', 'nga'],
    ['Pakistan', 'pak'],
    ['Philippines', 'phl'],
    ['State of Palestine', 'pse'],
    ['Sudan', 'sdn'],
    ['Somolia', 'som'],
    ['South Sudan', 'ssd'],
    ['Syria', 'syr'],
    ['Chad', 'tcd'],
    ['Turkey', 'tur'],
    ['Ukraine', 'ukr'],
    ['Venezuela', 'ven'],
    ['Yemen', 'yem'],
  ];

  const sources = [
    [
      'Administrative Boundaries',
      'OCHA Common Operational Datasets (CODs)',
      'https://cod.unocha.org',
    ],
    [
      'Roads, Waterways, Settlements, Ports, Education, Financial',
      'Humanitarian OpenStreetMap Team (HOT)',
      'https://data.humdata.org/organization/hot',
    ],
    ['Health', 'Healthsites.io', 'https://healthsites.io'],
    [
      'Protected Areas',
      'World Database on Protected Areas (WDPA)',
      'https://www.protectedplanet.net',
    ],
  ];
</script>

<svelte:head>
  <title>Maps | Fieldmaps.io</title>
</svelte:head>
<Header active="maps" />
<Body>
  <h1 class="has-text-centered">Atlas Maps</h1>
  <p class="has-text-centered">
    <img src="/img/atlas.png" alt="atlas" />
  </p>
  <p>
    These series of atlas reference maps have evolved organically overtime, starting with the South
    Sudan version, growing to include neighbouring countries, and finally to a larger sample of
    countries where structured source data was available. Ultimately, maintaining separate code
    bases for each country became more difficult as the list grew, and it was clear a new approach
    would be needed.
  </p>
  <p>
    Development on country-level maps listed below has been paused since January 2020 to focus on
    building code foundations for a unified, global version of these maps. From lessons learned in
    the field, the emphasis on this new version will be for searching names, discovering new
    locations, and providing tools to share precise location references between remote teams,
    sensitive to low-bandwidth conditions. This page will be updated when the new Global Atlas map
    is available, planned for early 2022, with a development preview available here:{' '}
    <a href="https://atlas.fieldmaps.io/">atlas.fieldmaps.io</a>
  </p>
  <h2 class="has-text-centered">Sources</h2>
  <div class="table-container">
    <table class="table">
      <thead>
        <tr>
          <th>Layer</th>
          <th>URL</th>
        </tr>
      </thead>
      <tbody>
        {#each sources as [layer, source, url]}
          <tr>
            <td>{layer}</td>
            <td>
              <a href={url}>{source}</a>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
  <h2 class="has-text-centered">Maps</h2>
  <div class="table-container">
    <table class="table">
      <thead>
        <tr>
          <th>ISO-3</th>
          <th>Name</th>
          <th>Offline-Enabled Map</th>
          <th>Base Map</th>
          <th>Vector Tiles</th>
        </tr>
      </thead>
      <tbody>
        {#each countries as [name, code]}
          <tr>
            <td>{code.toUpperCase()}</td>
            <td>{name}</td>
            <td>
              <a href={`https://atlas.fieldmaps.io/${code}/`} target="_blank">
                {`atlas.fieldmaps.io/${code}`}
              </a>
            </td>
            <td>
              <a href={`https://atlas.fieldmaps.io/styles/v1/${code}/default.json`} target="_blank">
                {`[Style URL]`}
              </a>
            </td>
            <td>
              <a href={`https://atlas.fieldmaps.io/v4/${code}.json`} target="_blank">
                {`[TileJSON]`}
              </a>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</Body>
<Footer />

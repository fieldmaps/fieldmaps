<script>
  const countries = [
    ["Afghanistan", "afg"],
    ["Burundi", "bdi"],
    ["Burkina Faso", "bfa"],
    ["Central African Republic", "caf"],
    ["Côte d'Ivoire", "civ"],
    ["Cameroon", "cmr"],
    ["Democratic Republic of the Congo", "cod"],
    ["Columbia", "col"],
    ["Eritrea", "eri"],
    ["Ethiopia", "eth"],
    ["Haiti", "hti"],
    ["Iraq", "irq"],
    ["Lebanon", "lbn"],
    ["Lybia", "lby"],
    ["Mali", "mli"],
    ["Myanmar", "mmr"],
    ["Mozambique", "moz"],
    ["Niger", "ner"],
    ["Nigeria", "nga"],
    ["Pakistan", "pak"],
    ["Philippines", "phl"],
    ["State of Palestine", "pse"],
    ["Sudan", "sdn"],
    ["Somolia", "som"],
    ["South Sudan", "ssd"],
    ["Syria", "syr"],
    ["Chad", "tcd"],
    ["Turkey", "tur"],
    ["Ukraine", "ukr"],
    ["Venezuela", "ven"],
    ["Yemen", "yem"]
  ];
  const data = [
    [
      "Administrative Boundaries",
      "OCHA Common Operational Datasets (CODs)",
      "https://data.humdata.org/search?ext_cod=1"
    ],
    [
      "Roads, Waterways, Settlements, Ports, Education, Financial",
      "Humanitarian OpenStreetMap Team (HOT)",
      "https://data.humdata.org/organization/hot"
    ],
    ["Health", "Healthsites.io", "https://healthsites.io"],
    [
      "Protected Areas",
      "World Database on Protected Areas (WDPA)",
      "https://www.protectedplanet.net"
    ]
  ];
</script>

<svelte:head>
  <title>Maps | Fieldmaps.io</title>
</svelte:head>

<div class="content">
  <p>
    Development on country-level maps has been paused to focus on curating
    global datasets. A future atlas version is being planned to consolidate the
    following into a single product.
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
        {#each data as [layer, source, url]}
          <tr>
            <td>{layer}</td>
            <td>
              <a href={url} target="_blank">{source}</a>
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
          <th>Country</th>
          <th>Code</th>
          <th>Offline-Enabled Map</th>
          <th>Base Map</th>
          <th>Vector Tiles</th>
        </tr>
      </thead>
      <tbody>
        {#each countries as [name, code]}
          <tr>
            <td>{name}</td>
            <td>{code.toUpperCase()}</td>
            <td>
              <a href={`https://atlas.fieldmaps.io/${code}/`} target="_blank">
                {`atlas.fieldmaps.io/${code}`}
              </a>
            </td>
            <td>
              <a
                href={`https://atlas.fieldmaps.io/styles/v1/${code}/default.json`}
                target="_blank">
                {`[Style URL]`}
              </a>
            </td>
            <td>
              <a
                href={`https://atlas.fieldmaps.io/v4/${code}.json`}
                target="_blank">
                {`[TileJSON]`}
              </a>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>

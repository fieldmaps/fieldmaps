<script lang="ts">
  const wlds = {
    intl: 'International',
    all: 'All',
    land: 'Land',
  };

  interface Props {
    data: any[];
    adm0?: boolean;
  }

  let { data, adm0 = false }: Props = $props();
</script>

<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>{adm0 ? 'World View' : 'Level'}</th>
        <th>GeoParquet (cloud-native)</th>
        <th>Geopackage (QGIS)</th>
        <th>Geodatabase (ArcGIS)</th>
      </tr>
    </thead>
    <tbody>
      {#each data as x}
        {#if x.wld !== 'land'}
          <tr>
            <td>{x.adm === 0 ? wlds[x.wld] : 'ADM 0-' + x.adm}</td>
            <td><a href={x.a_parquet}>Parquet</a></td>
            <td><a href={x.a_gpkg}>GPKG</a></td>
            <td><a href={x.a_gdb}>GDB</a></td>
          </tr>
        {/if}
      {/each}
    </tbody>
  </table>
</div>

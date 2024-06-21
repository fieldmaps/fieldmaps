<script lang="ts">
  const wlds = {
    intl: 'International',
    all: 'All',
    land: 'Land',
  };

  export let data: any[];
  export let adm0 = false;
</script>

<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>{adm0 ? 'World View' : 'Level'}</th>
        <th>Polygons</th>
        <th>Lines</th>
        <th>Points</th>
      </tr>
    </thead>
    <tbody>
      {#each data as x}
        {#if x.wld !== 'land'}
          <tr>
            <td>{x.adm === 0 ? wlds[x.wld] : 'ADM 0-' + x.adm}</td>
            <td>
              <a href={x.a_gpkg}>gpkg</a> |
              <a href={x.a_gdb}>gdb</a> |
              <a href={x.a_xlsx}>xlsx</a>
            </td>
            <td>
              <a href={x.l_gpkg}>gpkg</a> |
              <a href={x.l_gdb}>gdb</a> |
              <a href={x.l_xlsx}>xlsx</a>
            </td>
            <td>
              <a href={x.p_gpkg}>gpkg</a> |
              <a href={x.p_gdb}>gdb</a> |
              <a href={x.p_xlsx}>xlsx</a>
            </td>
          </tr>
        {/if}
      {/each}
    </tbody>
  </table>
</div>

<script lang="ts">
  const wlds = {
    intl: 'International',
    all: 'All',
    usa: 'USA',
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
        <th>UN WPP</th>
        <th>Meta / Facebook</th>
        <th>WorldPop</th>
      </tr>
    </thead>
    <tbody>
      {#each data as x}
        <tr>
          <td>{x.adm === 0 ? 'ADM 0' : 'ADM 0-' + x.adm}</td>
          <td>
            <a href={x.u_xlsx}>xlsx</a> |
            <a href={x.u_csv}>csv</a> |
            <a href={x.u_json}>json</a>
          </td>
          <td>
            <a href={x.m_xlsx}>xlsx</a> |
            <a href={x.m_csv}>csv</a> |
            <a href={x.m_json}>json</a>
          </td>
          <td>
            <a href={x.w_xlsx}>xlsx</a> |
            <a href={x.w_csv}>csv</a> |
            <a href={x.w_json}>json</a>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>

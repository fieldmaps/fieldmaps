<script lang="ts">
  export let data: any[];
</script>

<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>Level</th>
        <th>Excel</th>
        <th>CSV</th>
      </tr>
    </thead>
    <tbody>
      {#each data as x}
        <tr>
          <td>{x.adm === 0 ? 'ADM 0' : 'ADM 0-' + x.adm}</td>
          <td><a href={x.m_xlsx}>XLSX</a></td>
          <td><a href={x.w_csv}>CSV</a></td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>

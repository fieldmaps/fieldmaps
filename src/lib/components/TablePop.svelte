<script lang="ts">
  export let data: any[];
</script>

<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>Level</th>
        <!-- <th>Common Operational Datasets</th> -->
        <th>Meta / Facebook</th>
        <th>WorldPop</th>
      </tr>
    </thead>
    <tbody>
      {#each data as x}
        <tr>
          <td>{x.adm === 0 ? 'ADM 0' : 'ADM 0-' + x.adm}</td>
          <!-- <td>
            <a href={x.c_xlsx}>xlsx</a> |
            <a href={x.c_csv}>csv</a> |
            <a href={x.c_json}>json</a>
          </td> -->
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

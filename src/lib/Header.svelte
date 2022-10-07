<script lang="ts">
  export let active: string;
</script>

<div class="tabs is-centered">
  <ul>
    <li class={active === '' ? 'is-active' : ''}>
      <a href="/">home</a>
    </li>
    <li class={active === 'data' ? 'is-active' : ''}>
      <a href="/data">data</a>
    </li>
    <li class={active === 'maps' ? 'is-active' : ''}>
      <a href="/maps">maps</a>
    </li>
    <li class={active === 'about' ? 'is-active' : ''}>
      <a href="/about">about</a>
    </li>
  </ul>
</div>

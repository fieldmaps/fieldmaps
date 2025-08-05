<script lang="ts">
  interface Props {
    active: string;
  }

  let { active }: Props = $props();
</script>

<div class="tabs is-toggle is-centered">
  <ul>
    <li class={active === '' ? 'is-active' : ''}>
      <a href="/data">edge-matched</a>
    </li>
    <li class={active === 'adm0' ? 'is-active' : ''}>
      <a href="/data/adm0">adm0</a>
    </li>
    <li class={active === 'cod' ? 'is-active' : ''}>
      <a href="/data/cod">cod</a>
    </li>
    <li class={active === 'geoboundaries' ? 'is-active' : ''}>
      <a href="/data/geoboundaries">geoboundaries</a>
    </li>
  </ul>
</div>

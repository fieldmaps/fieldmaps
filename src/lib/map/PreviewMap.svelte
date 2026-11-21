<script lang="ts">
  import * as maplibregl from "maplibre-gl";
  import "maplibre-gl/dist/maplibre-gl.css";
  import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
  import { Protocol } from "pmtiles";
  import { buildStyle, globeFitZoom, readColors } from "./style";

  interface Props {
    center?: [number, number];
    zoom?: number;
    interactive?: boolean;
    labels?: boolean;
    target?: { center: [number, number]; zoom: number } | null;
  }

  let {
    center = [20, 10],
    zoom,
    interactive = true,
    labels = true,
    target = null,
  }: Props = $props();
  let container: HTMLDivElement;
  let map = $state.raw<maplibregl.Map | null>(null);

  $effect(() => {
    maplibregl.setWorkerUrl(workerUrl);
    const protocol = new Protocol();
    maplibregl.addProtocol("pmtiles", protocol.tile);
    const m = new maplibregl.Map({
      container,
      style: buildStyle(readColors(), { labels }),
      center,
      zoom: zoom ?? globeFitZoom(container),
      interactive,
      attributionControl: { compact: true },
    });
    if (interactive) m.addControl(new maplibregl.NavigationControl({ showCompass: false }));
    map = m;
    const resize = new ResizeObserver(() => m.resize());
    resize.observe(container);
    return () => {
      resize.disconnect();
      m.remove();
      maplibregl.removeProtocol("pmtiles");
    };
  });

  $effect(() => {
    if (map && target) map.flyTo({ center: target.center, zoom: target.zoom, duration: 2500 });
  });
</script>

<div class="map" bind:this={container}></div>

<style>
  .map {
    width: 100%;
    height: 100%;
  }
</style>

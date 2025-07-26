<script lang="ts">
  import Body from '$lib/components/Body.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Header from '$lib/components/Header.svelte';
</script>

<svelte:head>
  <title>Home | Fieldmaps.io</title>
</svelte:head>
<Header active="" />
<Body>
  <h1 class="has-text-centered">Humanitarian Reference Maps</h1>
  <p>
    Fieldmaps is an initiative designed to address the needs of humanitarian field workers operating
    in environments where data quality is variable, connectivity is sporadic, or where the context
    changes frequently. It looks to consolidate work that has already been done within the
    humanitarian community into living products designed for daily use. Beyond creating tools for
    end-users, a primary focus is promoting inter-agency data sharing.
  </p>
  <h2 class="has-text-centered">Data</h2>
  <p class="has-text-centered">
    <a href="/data">
      <img src="/img/coverage.png" alt="dataset coverage" />
    </a>
  </p>
  <p>
    The first part of this project is to create a living database that reflects the best available
    reference data from multiple sources into a common format that is easy to use. The approach
    taken here is to start with a baseline, typically OpenStreetMap, adding national sources that
    have been reviewed by a UN agency, NGO, or other humanitarian actor.
  </p>
  <p>
    To begin, work has been done cleaning up administrative boundaries to create a global
    edge-matched layer to be used as a foundation for additional layers on top. This database starts
    with countries which have undergone validation by UN OCHA for use as a common operational
    dataset (COD). These datasets have been reviewed for quality and consistency at the national
    level, so they are well aligned to fit into a global model with minimal transformations. For
    countries not covered, geoBoundaries is used as a gap-filler until more authoritative sources
    are available.
  </p>
  <h2 class="has-text-centered">Maps</h2>
  <p class="has-text-centered">
    <a href="/maps">
      <img src="/img/atlas-ssd.png" alt="atlas map" />
    </a>
  </p>
  <p>
    The second part of this project strives to make dense and technical data accessible to the
    widest possible audience. This comes from lessons learned in South Sudan and other countries in
    the region, where extremely low bandwidth and a lack of geospatial expertise made it difficult
    to put highly detailed databases into common use. A recurring problem was sharing datasets
    containing 10,000+ populated places among field teams, each trying to communicate back complex
    patterns of displacement between specific locations, often sharing similar colloquial names.
  </p>
  <h2 class="has-text-centered">Roadmap</h2>
  <p>The following slides show the roadmap for what the future of FieldMaps could expand into:</p>
  <p class="has-text-centered">
    <iframe
      src="https://docs.google.com/presentation/d/e/2PACX-1vSt7NyWPBZhD250rw_mbyv3XtjCT6m0HiE3L1kpP1Wowlm9My6R4qZVZiREIvwyO_UZDVwe0TGsHXJF/embed?start=false&loop=false&delayms=3000"
      title="Google Slides"
      frameborder="0"
      width="960"
      height="569"
      allowfullscreen
      mozallowfullscreen
      webkitallowfullscreen
></iframe>
  </p>
</Body>
<Footer />

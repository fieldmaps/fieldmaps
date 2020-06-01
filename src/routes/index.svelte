<svelte:head>
  <title>Home | Fieldmaps.io</title>
</svelte:head>

<div class="content">
  <h1 class="has-text-centered">Humanitarian Reference Maps</h1>
  <p>
    Fieldmaps is an ongoing project designed to address the needs of
    humanitarian field workers operating in environments where data quality is
    variable, connectivity is sporadic, or where the context changes frequently.
    It looks to consolidate work that has already been done within the
    humanitarian community into living products designed for daily use. Beyond
    creating tools for end-users, a primary focus is promoting inter-agency data
    sharing. Although the decentralization of field responses provides a great
    deal of adaptability and flexibility, a global data model can provide a
    useful framework for showing the bigger picture that emerges between
    organizations and countries.
  </p>
  <h2 class="has-text-centered">Data</h2>
  <a href="/data">
    <img
      src="https://raw.githubusercontent.com/fieldmaps/global-admin/master/images/coverage.png"
      alt="dataset coverage" />
  </a>
  <p>
    The first part of this project is to create a living database that reflects
    the "best available" reference data from multiple sources into a common
    format that is easy to use. The approach taken here is to start with a
    baseline, typically OpenStreetMap, adding national sources that have been
    reviewed by a UN agency, NGO, or other humanitarian actor.
  </p>
  <p>
    The first product produced using this model is the
    <a href="https://github.com/fieldmaps/global-admin">Global Admin</a>
    geodatabase. This database starts with
    <a href="https://gadm.org/data.html">GADM</a>
    , which provides a normalized schema, and builds on top of this by adding
    countries which have undergone validation by UN OCHA for use as a common
    operational dataset (
    <a
      href="https://humanitarian.atlassian.net/wiki/spaces/imtoolbox/pages/42045911/COD+Overview">
      COD
    </a>
    ). These datasets have been reviewed for quality and consistency at the
    national level, so little extra effort needs to be made to align this with a
    global model. It can be
    <a href="https://data.fieldmaps.io/global-admin/wld.gpkg.zip">downloaded</a>
    right now for testing with desktop GIS software, although the dataset is
    still in beta.
  </p>
  <h2 class="has-text-centered">Maps</h2>
  <a href="/maps">
    <img src="/atlas-ssd.png" alt="atlas map" />
  </a>
  <p>
    The second part of this project strives to make highly dense and technical
    data accessible to the widest possible audience. This comes from lessons
    learned in South Sudan and other parts of Africa, where extremely low
    bandwidth and a lack of geospatial expertise made it difficult to put highly
    detailed databases into common use. A recurring problem was sharing a
    dataset with tens of thousands of populated places among dozens of field
    teams, each trying to communicate back complex patters of displacement
    between specific places.
  </p>
  <p>
    The first prototype map of this kind was built to pull vector tile data
    offline for local querying. The usefulness of such a tool inspired regional
    copies, which resulted in the current set of 31 maps last updated in January
    2020. From these experiences, a single unified reference map emerged as the
    ideal way to scale this type of product globally, prompting the beginning of
    work on the
    <a href="https://github.com/fieldmaps/global-admin">Global Admin</a>
    project. It's intended that this feedback loop of practical visualizations
    informing data standards continue, as the efforts between humanitarian
    agencies converge to create improved coordination tools for a better
    response.
  </p>
</div>

<script lang="ts">
  import Body from '$lib/Body.svelte';
  import Footer from '$lib/Footer.svelte';
  import Header from '$lib/Header.svelte';
</script>

<svelte:head>
  <title>About | Fieldmaps.io</title>
</svelte:head>
<Header active="about" />
<Body>
  <h1 class="has-text-centered">About me</h1>
  <p>
    I've been fascinated with putting maps on the internet since first doing this at university,
    which has led me to some wonderful and remote corners of the world. In the private sector,
    working with SparkGeo Consulting in northern Canada on web app development and geospatial
    analytics. In the humanitarian sector, with REACH Initiative on missions in Jordan, South Sudan,
    and Nigeria. In these field missions, I started getting involved with information management in
    multiple clusters and working groups. In particular, creating common operational datasets with
    OCHA had me realize how valuable this kind of core infrastructure is by the people who rely on
    them. I'm contributing to this project in my personal time as a way to continue collaboration
    with all the people I've been in touch with in the past. If you want to talk about any of the
    content on here, you can reach me at: fieldmaps(at)maxmalynowsky.com
  </p>
  <h2 class="has-text-centered">Acknowledgements</h2>
  <p>
    None of this would be possible without the generous support from the following organizations,
    who's members have been instrumental in sharing data and giving countless hours of help online:
  </p>
  <ul>
    <li>William & Mary Geospatial Evaluation and Observation Lab</li>
    <li>Columbia University Center for International Earth Science Information Network (CIESIN)</li>
    <li>UN Office for the Coordination of Humanitarian Affairs (OCHA)</li>
    <li>UN World Food Programme (WFP)</li>
    <li>The Centre for Humanitarian Data</li>
    <li>University of Georgia, Information Technology Outreach Services (ITOS)</li>
    <li>REACH Initiative</li>
    <li>MapAction</li>
    <li>CartONG</li>
  </ul>
</Body>
<Footer />

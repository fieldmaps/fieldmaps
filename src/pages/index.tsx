import React from 'react';

import Layout from '../components/layout';
import SEO from '../components/seo';

const IndexPage = () => (
  <Layout>
    <SEO title="Home" />
    <div className="content">
      <h1 className="has-text-centered">Common Operational Maps</h1>
      <p>
        Fieldmaps is a service built to address the needs of humanitarian field
        workers operating in environments where data quality is variable,
        connectivity is sporadic, or where the context changes frequently. This
        platform was originally conceived in South Sudan, where existing mapping
        services provided very little information about place names, including
        OpenStreetMap. When reading about locations in reports, it was often
        difficult to places these settlements on a map for additional context.
        Conversely, it was also hard to give an unambiguous reference to a place
        that could be communicated to a colleague. In South Sudan, there is a
        Mayom in almost every country, how do you specify which Mayom with
        absolute certainty? OCHA P-Codes have attempted to mitigate this problem
        by assigning unique identifiers to each area and settlement, but without
        advanced GIS knowledge, it was difficult to effectively utilize this in
        practice.
      </p>
      <p>
        A practical solution to this problem would need to fulfill two criteria.
        First, it would have to be easy enough so that any non-technical user
        could pick up the tool and begin using it with no prior training,
        precluding the use of anything involving Shapefiles or Geodatabases.
        Second, it would need to function completely offline and receive updates
        in low bandwidth environments, making options such as ArcGIS online and
        other internet heavy applications a poor fit. Given these constraints,
        the best fit was a Mapbox-GL map with all layers saved as files on the
        user's device, with individual files updating automatically when
        available online. With this approach working well in one country, this
        platform is now testing whether it possible to scale this solution
        globally for all countries.
      </p>
      <h2 className="has-text-centered">Phase 1</h2>
      <p>
        The first stage of this project is to engage with primary data producers
        in curating a repository of high quality geographic information for a
        baseline visualization. At the moment, the largest such initiative of
        this sort is the{' '}
        <a href="https://centre.humdata.org/introducing-the-hdx-data-grid-a-way-to-find-and-fill-data-gaps">
          HDX Data Grid
        </a>
        . Fieldmaps has been actively coordinating with HDX to incorporate their
        grid and provide feedback on the usefulness of their sources, as well as
        to improve quality through data cleaning. Other curated humanitarian
        data sources include <a href="https://healthsites.io/">Healhsites.io</a>
        , a platform for healthcare workers to standardize and improve data
        around OpenStreetMap and trusted partner sources.
      </p>
      <p>
        To remain relevant in fast moving contexts, maps that utilize these
        sources need to be able to pull in updates on a daily basis if required.
        This necessitates an automated data pipeline that still retains enough
        flexibility to deal with irregularly formatted updates. The first draft
        of this pipeline has been completed, available{' '}
        <a href="https://github.com/fieldmaps/data">here</a>. By using Geopandas
        and QGIS batch configurations, most transformations can be performed in
        just a few clicks. Further work on this will improve the efficiency of
        spatial operations and move to a fully web-based service so a desktop
        computer is not required.
      </p>
      <h2 className="has-text-centered">Phase 2</h2>
      <p>
        Fieldmaps is currently in the stage of expanding the current series of
        reference templates to include all countries listed as operational in
        OCHA's <a href="https://tabsoft.co/2Q2mIGf">Tableau Dashboard</a>.
        Existing countries are also being updated to take advantage of
        additional data sources that have been recently curated. To deal with
        the increased density of data, maps will be updated with separate
        thematic layers, so each layer provides a clear high-level overview
        without other sources cluttering the map with an overload of
        information. The initial map series will pull in data from a relatively
        small number of sources. These include:
      </p>
      <ul>
        <li>
          <a href="https://data.humdata.org/search?ext_cod=1">
            OCHA COD administrative boundaries
          </a>
          ,
        </li>
        <li>
          <a href="https://healthsites.io">Healthsites.io</a> facility
          locations,
        </li>
        <li>
          <a href="https://www.protectedplanet.net">
            World Database on Protected Areas
          </a>
          , and
        </li>
        <li>
          <a href="https://data.humdata.org/organization/hot">
            Humanitarian OpenStreetMap Team (HOT)
          </a>{' '}
          filling in the rest of the layers.
        </li>
      </ul>
      <p>
        In the process of visualizing this data, gaps in geographic coverage
        should become more apparent. By coordinating with field workers
        in-country, these base sources can be improved over time by
        incorporating local sources endorsed by regional information management
        working groups. Two particular data sources that have been highlighted
        for additional local contributions are settlement and water sanitation
        &amp; hygiene infrastructure.
      </p>
      <h2 className="has-text-centered">Phase 3</h2>
      <p>
        Building a baseline of maps with commonly used sources is just one type
        of information product this site aims to provide. The final phase of
        Fieldmaps is to take the infrastructure developed for reference atlases,
        and open it up for all users to be able to create their own maps with
        similar functionality. While services like Google My Maps already exist
        for this purpose, it doesn't work offline, and it's not tightly
        integrated with other commonly used humanitarian data sources.
      </p>
    </div>
  </Layout>
);

export default IndexPage;

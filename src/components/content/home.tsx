import React from 'react';
import { Link } from 'gatsby';

export default () => (
  <>
    <h1 className="has-text-centered">Humanitarian Reference Maps</h1>
    <p>
      Fieldmaps is a personal project designed to address the needs of
      humanitarian field workers operating in environments where data quality is
      variable, connectivity is sporadic, or where the context changes
      frequently. It looks to consolidate work that has already been done within
      the humanitarian community into living products designed for daily use.
      Beyond creating tools for end-users, a primary focus is promoting
      inter-agency data sharing.
    </p>
    <h2 className="has-text-centered">Data</h2>
    <p className="has-text-centered">
      <Link to="/data">
        <img src="/img/coverage.png" alt="dataset coverage" />
      </Link>
    </p>
    <p>
      The first part of this project is to create a living database that
      reflects the best available reference data from multiple sources into a
      common format that is easy to use. The approach taken here is to start
      with a baseline, typically OpenStreetMap, adding national sources that
      have been reviewed by a UN agency, NGO, or other humanitarian actor.
    </p>
    <p>
      To begin, work has been done cleaning up administrative boundaries to
      create a global edge-matched layer to be used as a foundation for
      additional layers on top. This database starts with countries which have
      undergone validation by UN OCHA for use as a common operational dataset
      (COD). These datasets have been reviewed for quality and consistency at
      the national level, so they are well aligned to fit into a global model
      with minimal transformations. For countries not covered, geoBoundaries is
      used as a gap-filler until more authoritative sources are available.
    </p>
    <h2 className="has-text-centered">Maps</h2>
    <p className="has-text-centered">
      <Link to="/maps">
        <img src="/img/atlas-ssd.png" alt="atlas map" />
      </Link>
    </p>
    <p>
      The second part of this project strives to make dense and technical data
      accessible to the widest possible audience. This comes from lessons
      learned in South Sudan and other countries in the region, where extremely
      low bandwidth and a lack of geospatial expertise made it difficult to put
      highly detailed databases into common use. A recurring problem was sharing
      datasets containing 10,000+ populated places among field teams, each
      trying to communicate back complex patterns of displacement between
      specific locations, often sharing similar colloquial names.
    </p>
    <p>
      The first prototype map of this kind was built to pull data offline for
      local searches. The usefulness of such a tool inspired regional copies,
      which resulted in the current set of 31 maps last updated in January 2020.
      From these experiences, a single unified reference map emerged as the
      ideal way to scale this type of product globally, due to be completed in
      early 2021. The intenion is for this feedback loop of practical
      visualizations informing data standards to continue, as the efforts
      between humanitarian agencies continue to converge in creating improved
      coordination tools for a better response.
    </p>
  </>
);

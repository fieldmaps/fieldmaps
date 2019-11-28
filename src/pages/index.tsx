import React from 'react';

import Layout from '../components/layout';
import SEO from '../components/seo';

const IndexPage = () => (
  <Layout>
    <SEO title="Home" />
    <div className="content">
      <h1 className="has-text-centered">Fieldmaps.io</h1>
      <p>
        Welcome to Fieldmaps, a free service designed around making humanitarian
        data sources more accessible to end users. This project was started from
        experience in humanitarian field settings, where it can often be
        difficult to locate and utilize high quality data, especially with
        limited bandwidth or time. This project intends to actively curate
        sources and present them in a structured format so these decisions do
        not have to be made each time a new map is started, but rather offer a
        good baseline for others to start from.
      </p>
      <p>
        What this project is not trying to become is another repository for
        users to upload their data to, as there are already many of these across
        the internet. Aside from{' '}
        <a href="https://data.humdata.org">Humanitarian Data Exchange (HDX)</a>,
        the main repository of humanitarian data, there are much smaller
        thematic repositories scattered across the internet. Some of these focus
        around core cluster themes, such as{' '}
        <a href="https://www.waterpointdata.org/">
          Water Point Data Exchange (WPDx)
        </a>
        , global platform for sharing water point data encouraged by UNICEF, and{' '}
        <a href="https://healthsites.io/">Healhsites.io</a>, an interface for
        healthcare workers to improve and standardize metadata around
        OpenStreetMap. There are also many smaller repositories specific to
        organizations, and this project will look at regularly pulling from all
        these and determing the best way to combine them together.
      </p>
      <h2>Data</h2>
      <p>
        Currently displayed here are OCHA common operational datasets (CODs),
        administrative boundaries that has been downloaded from HDX and
        processed into multiple export formats. At the moment, this data is just
        used for testing purposes, with some known geometry and attribute errors
        that require minor corrections. This should not be used in place of
        official downloads from HDX right now.
      </p>
      <p>
        The intention behind this page is to simplify access to commonly used
        GIS data. The current layout is inspired by{' '}
        <a href="https://download.geofabrik.de">download.geofabrik.de</a>, a
        free service that simplifies access to OpenStreetMap data. At the
        moment, only a partial OCHA COD list has been curated and linked,
        however additional data sources are planned to be added in the future.
        These additional sources include:
      </p>
      <ul>
        <li>Settlements</li>
        <li>Roads</li>
        <li>Rivers</li>
        <li>Lakes</li>
        <li>Parks</li>
      </ul>
      <p>
        By listing this data in pre-processed formats, it should make it easier
        to recreate designs such as those listed on the maps page, so anyone can
        use this as a starting point for their own work. While some sources are
        officially endorsed, such as COD boundaries, other data that is required
        for basic reference maps can be more difficult hard to find in good
        quality or extract in a useful format.
      </p>
      <p>
        From experience, some data sources provide good global coverage, and it
        is planned for them to be bulk extracted and processed to individual
        country levels at regular intervals. These sources include{' '}
        <a href="https://openstreetmap.org">OpenStreetMap</a> for roads,{' '}
        <a href="https://www.hydrosheds.org/page/hydrorivers">HydroRIVERS</a>{' '}
        for rivers,{' '}
        <a href="https://www.hydrosheds.org/page/hydrolakes">HydroLAKES</a> for
        water bodies, and{' '}
        <a href="https://www.protectedplanet.net">
          World Database for Protected Areas
        </a>{' '}
        for parks. The value added services this project intends to provide is
        simple clipping, attribute joining, and other small but helpful quality
        of life improvements that allow users to get started using these sources
        as quickly as possible.
      </p>
      <h2>Maps</h2>
      <p>
        Although technical users may prefer having access to source data so they
        can customize outputs for their needs, non-technical users mostly prefer
        a ready to use app that can be used immidiately without any
        configuration. The maps currently listed here were created from the
        experience of field workers asking for an easy way to search for
        settlements without having to load a shapefile into QGIS. These
        applications are also completely self contained, and can be used offline
        or when internet is poor.
      </p>
      <p>
        Although the map list currently shows only settlements, other data
        sources are frequently requested in a similar format, such as water
        points, health clinics, and schools. These types of maps are being
        considered for the future to make more types of datasets easily
        accessible for reference and decision making.
      </p>
    </div>
  </Layout>
);

export default IndexPage;

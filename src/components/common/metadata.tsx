import React from 'react';
import Helmet from 'react-helmet';

const url = 'https://fieldmaps.io/';
const img = 'https://fieldmaps.io/img/atlas-ssd.png';
const title = 'Fieldmaps.io — Humanitarian Reference Maps and Data';
const description =
  'Mobile, offline, interactive reference maps for humanitarian use and globally aggregated data catalogues.';

export default ({ page }) => (
  <Helmet>
    <title>{page} | Fieldmaps.io</title>
    <link rel="icon" type="image/png" href="img/logo-192.png" />
    <meta name="title" content={title} />
    <meta name="description" content={description} />
    <meta property="og:type" content="website" />
    <meta property="og:url" content={url} />
    <meta property="og:title" content={title} />
    <meta property="og:description" content={description} />
    <meta property="og:image" content={img} />
    <meta property="twitter:card" content="summary_large_image" />
    <meta property="twitter:url" content={url} />
    <meta property="twitter:title" content={title} />
    <meta property="twitter:description" content={description} />
    <meta property="twitter:image" content={img} />
  </Helmet>
);

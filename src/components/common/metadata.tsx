import React from 'react';
import Helmet from 'react-helmet';

const url = 'https://fieldmaps.io/';
const img = 'https://fieldmaps.io/img/atlas-ssd-preview.png';
const title = 'Fieldmaps.io — Humanitarian Maps & Data';
const description =
  'Mobile, offline, interactive reference maps & globally aggregated datasets for humanitarian use.';

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
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:url" content={url} />
    <meta name="twitter:title" content={title} />
    <meta name="twitter:description" content={description} />
    <meta name="twitter:image" content={img} />
    <script
      defer
      src="/cf.js"
      data-cf-beacon='{"token": "4c2d512f347d47b5bf303b367560bcfd"}'
    />
  </Helmet>
);

module.exports = {
  siteMetadata: {
    title: 'Fieldmaps.io',
    description:
      'Mobile, offline, interactive reference maps for humanitarian use',
    author: '@gatsbyjs',
  },
  plugins: [
    {
      resolve: 'gatsby-plugin-google-analytics',
      options: {
        trackingId: 'UA-40353241-6',
      },
    },
    {
      resolve: 'gatsby-plugin-offline',
      options: {
        workboxConfig: {
          offlineGoogleAnalytics: true,
        },
      },
    },
    {
      resolve: 'gatsby-source-filesystem',
      options: {
        name: 'images',
        path: `${__dirname}/src/images`,
      },
    },
    {
      resolve: 'gatsby-plugin-manifest',
      options: {
        name: 'Fieldmaps.io',
        short_name: 'Fieldmaps.io',
        start_url: '/',
        background_color: '#78B5D6',
        theme_color: '#78B5D6',
        display: 'minimal-ui',
        icon: 'src/images/icon.svg',
      },
    },
    'gatsby-transformer-sharp',
    'gatsby-plugin-react-helmet',
    'gatsby-plugin-sharp',
    'gatsby-plugin-typescript',
    'gatsby-plugin-sass',
    'gatsby-plugin-netlify',
  ],
};

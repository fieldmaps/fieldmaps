import React from 'react';
import TableDest from '../common/table-dest';
import data from '../../../data/adm0.json';

const dataUrl = 'https://data.fieldmaps.io/adm0';
const options = {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  timeZone: 'UTC',
};

export default () => {
  return (
    <>
      <h1 className="has-text-centered">International Boundaries</h1>
      <p className="has-text-centered">
        <img src="/img/adm0.png" alt="adm0" />
      </p>
      <p>
        Updated: {new Date(data[0]?.date).toLocaleDateString('en-GB', options)}
      </p>
      <h2>Detailed</h2>
      <p>
        Very high resolution boundaries using{' '}
        <a href="https://osmdata.openstreetmap.de/data/land-polygons.html">
          OpenStreetMap
        </a>{' '}
        for coastline data,{' '}
        <a href="https://hiu.state.gov/data/">
          U.S. Department of State Large Scale International Boundaries (LSIB)
        </a>{' '}
        for international boundaries, and{' '}
        <a href="https://unstats.un.org/unsd/methodology/m49/overview/">
          United Nations Statistics Division M49
        </a>{' '}
        for attributes. See{' '}
        <a href="https://github.com/fieldmaps/adm0-generator">GitHub</a> for
        technical information on how this layer is made.
      </p>
      <p>
        This ADM0 layer comes in several versions to represent different world
        views of disputed areas. Starting with the "All" version, areas are
        dissolved together based on varying international recognition. The
        following preset world views are available for download:
      </p>
      <ul>
        <li>
          <b>International</b>: A balanced world view for use by international
          non-governmental organizations. Disputed areas follow recommended
          representation used by the{' '}
          <a href="https://geoservices.un.org/Html5Viewer/index.html?viewer=clearmap">
            UN Clear Map
          </a>
          . UN agencies should use official layers at the{' '}
          <a href="https://geoservices.un.org/webapps/geohub/">
            UN Geospatial Hub
          </a>
          .
        </li>
        <li>
          <b>All</b>: A conservative world view that dissagregates disputed
          areas. Useful if applying individual customization outside the presets
          generated here.
        </li>
        <li>
          <b>United States</b>: World view of the United States as represented
          in the original Large Scale International Boundaries (LSIB) layer.
        </li>
        <li>
          <b>Land</b>: Only shorline data, recommended for using with point and
          line layers above for cartographic applications.
        </li>
      </ul>
      <TableDest adm0 data={data.filter(x => x.grp === 'detailed')} />
      <h2>Simplified</h2>
      <p>
        The following uses OpenStreetMap simplified coastlines (~30MB) instead
        of originals (&gt;1GB), LSIB layer is unchanged.
      </p>
      <TableDest adm0 data={data.filter(x => x.grp === 'simplified')} />
      <p>
        Download metadata tables as: <a href={dataUrl + '.json'}>json</a> |{' '}
        <a href={dataUrl + '.csv'}>csv</a> |{' '}
        <a href={dataUrl + '.xlsx'}>xlsx</a>
      </p>
    </>
  );
};

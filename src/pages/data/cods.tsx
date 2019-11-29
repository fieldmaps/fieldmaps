import React from 'react';

import Layout from '../../components/layout';
import SEO from '../../components/seo';

const countries = [
  ['Afghanistan', 'afg'],
  ['Burundi', 'bdi'],
  ['Burkina Faso', 'bfa'],
  ['Central African Republic', 'caf'],
  ["Côte d'Ivoire", 'civ'],
  ['Cameroon', 'cmr'],
  ['Democratic Republic of the Congo', 'cod'],
  ['Columbia', 'col'],
  ['Eritrea', 'eri'],
  ['Ethiopia', 'eth'],
  ['Haiti', 'hti'],
  ['Irap', 'irq'],
  ['Lebanon', 'lbn'],
  ['Lybia', 'lby'],
  ['Mali', 'mli'],
  ['Mozambique', 'moz'],
  ['Niger', 'ner'],
  ['Nigeris', 'nga'],
  ['Pakistan', 'pak'],
  ['State of Palestine', 'pse'],
  ['Sudan', 'sdn'],
  ['Somolia', 'som'],
  ['South Sudan', 'ssd'],
  ['Chad', 'tcd'],
  ['Tuekey', 'tur'],
  ['Yemen', 'yem'],
];

const SecondPage = () => (
  <Layout>
    <SEO title="Data" />
    <nav className="level">
      <div className="level-item">
        <a href="https://data.fieldmaps.io/hdx-cods/planet.gpkg">
          Download all data as GeoPackage
        </a>
      </div>
    </nav>
    <nav className="level">
      <div className="level-item">
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Country</th>
                <th>Code</th>
                <th>GeoPackage</th>
                <th>ESRI Shapefile</th>
                <th>Google Earth</th>
                <th>GeoJSON</th>
              </tr>
            </thead>
            <tbody>
              {countries.map(([name, code]) => (
                <tr key={code}>
                  <td>{name}</td>
                  <td>{code.toUpperCase()}</td>
                  <td>
                    <a
                      href={`https://data.fieldmaps.io/hdx-cods/gpkg/${code}.gpkg`}
                    >
                      [.gpkg]
                    </a>
                  </td>
                  <td>
                    <a
                      href={`https://data.fieldmaps.io/hdx-cods/shp/${code}_shp.zip`}
                    >
                      [.shp.zip]
                    </a>
                  </td>
                  <td>
                    <a
                      href={`https://data.fieldmaps.io/hdx-cods/kmz/${code}_kmz.zip`}
                    >
                      [.kmz.zip]
                    </a>
                  </td>
                  <td>
                    <a
                      href={`https://data.fieldmaps.io/hdx-cods/geojson/${code}_geojson.zip`}
                    >
                      [.geojson.zip]
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </nav>
  </Layout>
);

export default SecondPage;

import React from 'react';

import Layout from '../components/layout';
import SEO from '../components/seo';

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
  ['Iraq', 'irq'],
  ['Lebanon', 'lbn'],
  ['Lybia', 'lby'],
  ['Mali', 'mli'],
  ['Mozambique', 'moz'],
  ['Niger', 'ner'],
  ['Nigeria', 'nga'],
  ['Pakistan', 'pak'],
  ['State of Palestine', 'pse'],
  ['Sudan', 'sdn'],
  ['Somolia', 'som'],
  ['South Sudan', 'ssd'],
  ['Syria', 'syr'],
  ['Chad', 'tcd'],
  ['Turkey', 'tur'],
  ['Ukraine', 'ukr'],
  ['Venezuela', 'ven'],
  ['Yemen', 'yem'],
];

const SecondPage = () => (
  <Layout>
    <SEO title="Data" />
    <nav className="level">
      <div className="level-item">
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Country</th>
                <th>Code</th>
                <th>Atlas</th>
              </tr>
            </thead>
            <tbody>
              {countries.map(([name, code]) => (
                <tr key={code}>
                  <td>{name}</td>
                  <td>{code.toUpperCase()}</td>
                  <td>
                    <a
                      href={`https://${code}-atlas.fieldmaps.io`}
                      target="_blank"
                    >
                      {`${code}-atlas.fieldmaps.io`}
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

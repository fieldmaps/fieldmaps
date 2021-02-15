import React from 'react';

const data = [
  ['Boundary Polygons', 'polygons', '4.60 GB', '2.02 GB'],
  ['Cartographic Lines', 'lines', '751 MB', '343 MB'],
  ['Label Points', 'points', '19.9 MB', '11.5 MB'],
];

const sources = [
  [
    'Coastlines',
    'OSM',
    'https://osmdata.openstreetmap.de/data/land-polygons.html',
  ],
  ['Admin 0', 'UN GIS', 'https://data.humdata.org/dataset/united-nations-map'],
  ['Admin 1-4 Primary', 'OCHA', 'https://cod.unocha.org'],
  ['Admin 1-4 Secondary', 'GADM', 'https://gadm.org/data.html'],
];

export default () => (
  <>
    <h1 className="has-text-centered">Global Edge-Matched Admin Data</h1>
    <p>
      The Global Admin project is a data processing pipeline designed to take
      the best available administration boundary information from multiple
      sources (OCHA, government, OSM, GADM, etc), aggregating them into a single
      edge-matched dataset with a common schema using an automated methodology.
      The most detailed admin level available is used, ranging from 0-4
      depending on the source. This dataset uses ISO-3 codes as the primary unit
      of edge-matching, with{' '}
      <a href="https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/blob/master/all/all.csv">
        249
      </a>{' '}
      currently used (not including disputed areas). Of these, 227 ISO-3 codes
      have subdivisions available: 114 sourced from OCHA, 106 from GADM, and 7
      from public government data repositories. All these sources are matched to
      an admin 0 dataset produced by the UN Geospatial Information Section, and
      coastlines produced by OpenStreetMap. Data can be downloaded from the
      following links (updated weekly), last updated Monday, 15 February, 2021:
    </p>
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>Layer (ADM 0-4)</th>
            <th>GeoPackage (GPKG)</th>
            <th>File Geodatabase (GDB)</th>
          </tr>
        </thead>
        <tbody>
          {data.map(([name, layer, size1, size2]) => (
            <tr key={layer}>
              <td>{name}</td>
              <td>
                <a
                  href={`https://data.fieldmaps.io/global-admin/wld_${layer}.gpkg.zip`}
                >
                  {`wld_${layer}.gpkg.zip (${size1})`}
                </a>
              </td>
              <td>
                <a
                  href={`https://data.fieldmaps.io/global-admin/wld_${layer}.gdb.zip`}
                >
                  {`wld_${layer}.gdb.zip (${size2})`}
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    <h2 className="has-text-centered">Sources</h2>
    <p>
      The following links point to data catalogues used for this project, all
      data manually downloaded, and some transformations performed. These are
      some of the modifications performed on each source as a pre-processing
      step:
      <ul>
        <li>
          <b>OCHA</b>: Boundary modifications are mostly limited to areas
          involving disputed boundaries, such as both Sudan and South Sudan
          claiming the Abyei Administrative Region. In this case, the area is
          removed from both countries when performing edge-matching, and
          represented as a disputed area in the admin 0 layer. In rare cases,
          topology cleaning is also required. For attributes that have not been
          formatted to the ITOS geodatabase standard, as defined by documents on{' '}
          <a href="https://github.com/UGA-ITOSHumanitarianGIS/mapservicedoc">
            GitHub
          </a>
          , tables are manually changed to match this so they can be
          automatically read.
        </li>
        <li>
          <b>GADM</b>: Lakes and water bodies are classified as administrative
          regions with no names in this dataset, and are therefore removed
          before performing edge-matching.
        </li>
      </ul>
    </p>
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>Layer</th>
            <th>Source</th>
          </tr>
        </thead>
        <tbody>
          {sources.map(([layer, source, url]) => (
            <tr>
              <td>{layer}</td>
              <td>
                <a href={url}>{source}</a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    <h2 className="has-text-centered">Boundary Normalization</h2>
    <p>
      A common problem of merging spatial data from different sources is the
      existence of gaps and overlaps between sources. There are many ways to
      address this problem, with the approach taken here being to generate
      borderless digital boundary files for each input. In this context, a
      digital boundary file is one that does not follow shorelines and
      international boundaries, but rather stretches out with simplified edges,
      intended for users to clip with their own shorelines and international
      boundaries. For example, Statistics Canada uses a digital boundary file
      when creating census blocks, later clipped with lakes and shorelines to
      derive a layer suitable for reference maps.
    </p>
    <p className="has-text-centered">
      <a href="https://www150.statcan.gc.ca/n1/pub/92-195-x/2011001/other-autre/carto-eng/carto-eng.htm">
        <img
          src="/img/cbf-vs-dbf.png"
          alt="cartographic vs digital boundary file"
        />
      </a>
    </p>
    <h2 className="has-text-centered">Attribute Normalization</h2>
    <p>
      Just as with boundaries, merging attribute columns between sources with
      different schemas need to be conditioned so that columns align with each
      other. The following schema is used.
    </p>
    <h3 className="has-text-centered">Repeating in layer</h3>
    <p>
      The following columns repeat for each higher level in an admin layer. An
      admin 2 layer will include attributes for adm2, adm1, and adm0. Replace
      the "X" with the indicated level.
    </p>
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>admX_id</td>
            <td>
              Automatically generated ID used for internal pipeline management.
            </td>
          </tr>
          <tr>
            <td>admX_ocha</td>
            <td>
              P-Code taken from OCHA sources. If not an OCHA source, a P-Code
              like ID is generated using the ISO-2 code.
            </td>
          </tr>
          <tr>
            <td>admX_name1</td>
            <td>
              Primary administrative region name. Uses the language defined by
              the "lang_name1" column.
            </td>
          </tr>
          <tr>
            <td>admX_name2</td>
            <td>
              Secondary administrative region name. Uses the language defined by
              the "lang_name2" column.
            </td>
          </tr>
          <tr>
            <td>admX_name3</td>
            <td>
              Tertiary administrative region name. Uses the language defined by
              the "lang_name3" column.
            </td>
          </tr>
          <tr>
            <td>admX_namea</td>
            <td>
              All other names listed for a region are combined together using
              the pipe ( | ) symbol.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <h3 className="has-text-centered">Once per layer</h3>
    <p>
      These columns only appear a single time per layer, providing layer
      metadata.
    </p>
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>lang_name1</td>
            <td>Primary language used for "admX_name1".</td>
          </tr>
          <tr>
            <td>lang_name2</td>
            <td>Secondary language used for "admX_name2".</td>
          </tr>
          <tr>
            <td>lang_name3</td>
            <td>Tertiary language used for "admX_name3".</td>
          </tr>
          <tr>
            <td>src_name</td>
            <td>One of: OCHA, GOVT, GADM.</td>
          </tr>
          <tr>
            <td>src_url</td>
            <td>Link where the original data source can be downloaded.</td>
          </tr>
          <tr>
            <td>src_date</td>
            <td>Date original dataset was produced.</td>
          </tr>
          <tr>
            <td>src_valid</td>
            <td>Last date original dataset was reviewed.</td>
          </tr>
          <tr>
            <td>adm_max</td>
            <td>
              Most detailed administrative level available for a particular
              ISO-3 region.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <h3 className="has-text-centered">Only in admin 0</h3>
    <p>These columns only appear in the admin 0 layer.</p>
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>adm0_fid</td>
            <td>
              Feature ID code used to differentiate states and self-governing
              territories sharing the same ISO-3 code.
            </td>
          </tr>
          <tr>
            <td>adm0_name</td>
            <td>
              Romanized name associated to the region defined by adm0_fid.
            </td>
          </tr>
          <tr>
            <td>adm0_label</td>
            <td>Map label to be used for a region defined by adm0_fid.</td>
          </tr>
          <tr>
            <td>adm0_cont</td>
            <td>Code of the continent a given ISO-3 belongs to.</td>
          </tr>
          <tr>
            <td>adm0_color</td>
            <td>
              When creating thematic maps, features sharing the same value for
              this column should be coloured together.
            </td>
          </tr>
          <tr>
            <td>adm0_stsc</td>
            <td>
              Indicates the sovereignty status code of the region given as an
              integer.
            </td>
          </tr>
          <tr>
            <td>adm0_stsn</td>
            <td>
              Indicates the sovereignty status of the region (State, Territory,
              Special Region, etc).
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </>
);

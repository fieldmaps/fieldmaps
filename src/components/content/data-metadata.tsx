import React from 'react';
import wldAdm0 from '../../../wld-adm0.json';

const wldAdm0Filtered = wldAdm0.filter(x => x.adm_max > 0);

export default () => (
  <>
    <h1 className="has-text-centered">Boundaries Metadata</h1>
    <p>
      For those looking to find out more information about the sources used in
      this dataset, the following table provides some additional details, also
      downloadable as a <a href="/wld-adm0.csv">CSV</a>. Columns provide the
      following information:
      <ul>
        <li>
          <b>ISO-3</b>: Code used for edge-matching. Clicking on the link
          downloads a GeoPackage (GPKG) containing the borderless boundaries
          generated with voronoi polygons, as described in the methodology
          section. These are the same files used in creating the final datasets
          listed in the overview section.
        </li>
        <li>
          <b>ISO-2</b>: Alternative code, commonly used by OCHA for creating
          their place codes (P-Codes). Clicking on the link downloads an ESRI
          File Geodatabase (GDB).
        </li>
        <li>
          <b>Name</b>: Admin 0 name as defined by the source. For OCHA sources,
          multiple languages are commonly available for countries. The first
          listed name is used here, usually one of the following Latin
          languages: English (EN), French (FR), Spanish (ES), or Portuguese
          (PT). GADM sources always use English names, which may not be the
          preferred country name.
        </li>
        <li>
          <b>ADM Levels</b>: Maximum number of admin levels found in the source.
        </li>
        <li>
          <b>Date</b>: Usually refers to when the original dataset was produced
          by the primary source, or when the last significant boundary changes
          were made by a reviewer.
        </li>
        <li>
          <b>Valid</b>: Date of last dataset review, where there may or may not
          have been minor changes and / or corrections.
        </li>
        <li>
          <b>Source</b>: Clicking on an OCHA or GOVT link will lead to the page
          containing an original dataset that can be downloaded. Sources listed
          with a dash are those from GADM, where the original is unknown, and
          last updated in 2018.
        </li>
      </ul>
    </p>
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>ISO-3</th>
            <th>ISO-2</th>
            <th>Name</th>
            <th>ADM Levels</th>
            <th>Date</th>
            <th>Valid</th>
            <th>Source</th>
          </tr>
        </thead>
        <tbody>
          {wldAdm0Filtered.map(row => (
            <tr key={row.adm0_id}>
              <td>
                <a
                  href={`https://data.fieldmaps.io/global-admin/voronoi/${row.adm0_id.toLowerCase()}.gpkg.zip`}
                >
                  {row.adm0_id}
                </a>
              </td>
              <td>
                <a
                  href={`https://data.fieldmaps.io/global-admin/voronoi/${row.adm0_id.toLowerCase()}.gdb.zip`}
                >
                  {row.adm0_ocha}
                </a>
              </td>
              <td>{row.adm0_name1}</td>
              <td>{row.adm_max}</td>
              <td>{row.src_name === 'GADM' ? '—' : row.src_date}</td>
              <td>{row.src_name === 'GADM' ? '—' : row.src_valid}</td>
              <td>
                {row.src_url ? (
                  row.src_name === 'GADM' ? (
                    '—'
                  ) : (
                    <a href={row.src_url}>{row.src_name}</a>
                  )
                ) : (
                  row.src_name
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </>
);

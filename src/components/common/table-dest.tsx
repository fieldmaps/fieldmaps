import React from 'react';

interface Props {
  data: any[];
  adm0?: boolean;
}

const wlds = {
  intl: 'International',
  all: 'All',
  usa: 'USA',
  chn: 'China',
  ind: 'India',
  land: 'Land',
};

export default ({ data, adm0 = false }: Props) => (
  <div className="table-container">
    <table className="table">
      <thead>
        <tr>
          <th>{adm0 ? 'World View' : 'Level'}</th>
          <th>Polygons</th>
          <th>Lines</th>
          <th>Points</th>
        </tr>
      </thead>
      <tbody>
        {data.map(x =>
          x.wld === 'land' ? (
            <tr key={x.id}>
              <td>{x.adm === 0 ? wlds[x.wld] : 'ADM 0-' + x.adm}</td>
              <td>
                <a href={x.a_gpkg}>gpkg</a> | <a href={x.a_shp}>shp</a>
              </td>
              <td></td>
              <td></td>
            </tr>
          ) : (
            <tr key={x.id}>
              <td>{x.adm === 0 ? wlds[x.wld] : 'ADM 0-' + x.adm}</td>
              <td>
                <a href={x.a_gpkg}>gpkg</a> | <a href={x.a_shp}>shp</a> |{' '}
                <a href={x.a_xlsx}>xlsx</a>
              </td>
              <td>
                <a href={x.l_gpkg}>gpkg</a> | <a href={x.l_shp}>shp</a> |{' '}
                <a href={x.l_xlsx}>xlsx</a>
              </td>
              <td>
                <a href={x.p_gpkg}>gpkg</a> | <a href={x.p_shp}>shp</a> |{' '}
                <a href={x.p_xlsx}>xlsx</a>
              </td>
            </tr>
          )
        )}
      </tbody>
    </table>
  </div>
);

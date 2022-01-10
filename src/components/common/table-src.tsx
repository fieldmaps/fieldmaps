import React from 'react';

interface Props {
  data: any[];
}

const options = {
  year: 'numeric',
  month: 'short',
  timeZone: 'UTC',
};

export default ({ data }: Props) => (
  <div className="table-container">
    <table className="table">
      <thead>
        <tr>
          <th>ISO-3</th>
          <th>ADM</th>
          <th>Name</th>
          <th>Date</th>
          <th>Update</th>
          <th>Source</th>
          <th>Extended</th>
          <th>Originals</th>
        </tr>
      </thead>
      <tbody>
        {data.map(x => (
          <tr key={x.id}>
            <td>{x.iso_3}</td>
            <td>{x.src_lvl}</td>
            <td>{x.adm0_name}</td>
            <td>{new Date(x.src_date).toLocaleDateString('en-US', options)}</td>
            <td>
              {new Date(x.src_update).toLocaleDateString('en-US', options)}
            </td>
            <td>
              <a href={x.src_url}>URL</a>
            </td>
            <td>
              <a href={x.e_gpkg}>gpkg</a> | <a href={x.e_shp}>shp</a> |{' '}
              <a href={x.e_xlsx}>xlsx</a>
            </td>
            <td>
              <a href={x.o_gpkg}>gpkg</a> | <a href={x.o_shp}>shp</a> |{' '}
              <a href={x.o_xlsx}>xlsx</a>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

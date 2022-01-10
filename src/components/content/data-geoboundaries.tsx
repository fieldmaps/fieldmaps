import React from 'react';
import TableSrc from '../common/table-src';
import data from '../../../data/geoboundaries.json';

const dataUrl = 'https://data.fieldmaps.io/geoboundaries';

export default () => {
  return (
    <>
      <h1 className="has-text-centered">geoBoundaries</h1>
      <p className="has-text-centered">
        <img src="/img/geoboundaries.png" alt="cod" />
      </p>
      <p>
        Visit <a href="https://www.geoboundaries.org/">geoboundaries.org</a> for
        the latest information about geoBoundaries layers. Data below is
        automatically downloaded from the geoBoundaries API at the source URLs
        below before processed for edge matching. Extended layers can be
        downloaded and clipped to any ADM0, with the original layer available
        for reference.
      </p>
      <TableSrc data={data} />
      <p>
        Download metadata table as: <a href={dataUrl + '.json'}>json</a> |{' '}
        <a href={dataUrl + '.csv'}>csv</a> |{' '}
        <a href={dataUrl + '.xlsx'}>xlsx</a>
      </p>
    </>
  );
};

import React from 'react';
import TableSrc from '../common/table-src';
import data from '../../../data/cod.json';

const dataUrl = 'https://data.fieldmaps.io/cod';

export default () => {
  return (
    <>
      <h1 className="has-text-centered">Common Operational Datasets</h1>
      <p className="has-text-centered">
        <img src="/img/cod.png" alt="cod" />
      </p>
      <p>
        Visit <a href="https://cod.unocha.org/">cod.unocha.org</a> for the
        latest information about OCHA COD layers. Data below is manually
        downloaded from The Humanitarian Data Exchange at the source URLs below
        before processed for edge matching. Extended layers can be downloaded
        and clipped to any ADM0, with the original layer available for
        reference.
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

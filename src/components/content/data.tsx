import React from 'react';
import TableDest from '../common/table-dest';
import data from '../../../data/edge-matched.json';

const dataUrl = 'https://data.fieldmaps.io/edge-matched';
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
      <h1 className="has-text-centered">Edge-Matched Boundaries</h1>
      <p className="has-text-centered">
        <img src="/img/edge-matched.png" alt="edge-matched" />
      </p>
      <p>
        Updated: {new Date(data[0].date).toLocaleDateString('en-GB', options)}
      </p>
      <h2>Humanitarian</h2>
      <p>
        Uses Common Operational Datasets (COD) when available, falling back to
        geoBoundaries for regions without coverage. Represents the latest
        available data for humanitarian operational use, cannot be used for
        other applications. Uses the "International" ADM0 world view for
        edge-matching.
      </p>
      <TableDest data={data.filter(x => x.grp === 'humanitarian')} />
      <h2>Open</h2>
      <p>
        Uses geoBoundaries exclusively, representing data suitable for most
        purposes, academic or commercial. Requires attribution to geoBoundaries.
        Uses the "International" ADM0 world view for edge-matching.
      </p>
      <TableDest data={data.filter(x => x.grp === 'open')} />
      <p>
        Download metadata tables as: <a href={dataUrl + '.json'}>json</a> |{' '}
        <a href={dataUrl + '.csv'}>csv</a> |{' '}
        <a href={dataUrl + '.xlsx'}>xlsx</a>
      </p>
      See <a href="https://github.com/fieldmaps/edge-extender">GitHub</a> for
      technical information on how edge-matching is performed.
    </>
  );
};

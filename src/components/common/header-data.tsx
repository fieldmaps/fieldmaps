import React from 'react';
import { Link } from 'gatsby';

export default ({ active }) => (
  <div className="tabs is-toggle is-centered">
    <ul>
      <li className={active === '' ? 'is-active' : ''}>
        <Link to="/data">edge-matched</Link>
      </li>
      <li className={active === 'adm0' ? 'is-active' : ''}>
        <Link to="/data/adm0">adm0</Link>
      </li>
      <li className={active === 'cod' ? 'is-active' : ''}>
        <Link to="/data/cod">cod</Link>
      </li>
      <li className={active === 'geoboundaries' ? 'is-active' : ''}>
        <Link to="/data/geoboundaries">geoboundaries</Link>
      </li>
    </ul>
  </div>
);

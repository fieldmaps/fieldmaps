import React from 'react';
import { Link } from 'gatsby';

export default ({ active }) => (
  <div className="tabs is-toggle is-centered">
    <ul>
      <li className={active === '' ? 'is-active' : ''}>
        <Link to="/data">overview</Link>
      </li>
      <li className={active === 'methodology' ? 'is-active' : ''}>
        <Link to="/data/methodology">methodology</Link>
      </li>
      <li className={active === 'metadata' ? 'is-active' : ''}>
        <Link to="/data/metadata">metadata</Link>
      </li>
    </ul>
  </div>
);

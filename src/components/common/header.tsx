import React from 'react';
import { Link } from 'gatsby';

export default ({ active }) => (
  <div className="tabs is-centered">
    <ul>
      <li className={active === '' ? 'is-active' : ''}>
        <Link to="/">home</Link>
      </li>
      <li className={active === 'data' ? 'is-active' : ''}>
        <Link to="/data">data</Link>
      </li>
      <li className={active === 'maps' ? 'is-active' : ''}>
        <Link to="/maps">maps</Link>
      </li>
      <li className={active === 'about' ? 'is-active' : ''}>
        <Link to="/about">about</Link>
      </li>
    </ul>
  </div>
);

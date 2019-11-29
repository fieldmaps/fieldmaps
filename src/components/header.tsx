import React, { useState, useEffect } from 'react';
import { Link } from 'gatsby';

import logo from '../images/icon.svg';

interface State {
  menuOpen: boolean;
}

const onClick = (state: State, setState: Function) =>
  setState(state => ({ ...state, menuOpen: !state.menuOpen }));

const componentDidMount = setState => {
  const { pathname } = window.location;
  setState(state => ({ ...state, pathname }));
};

const PageHeader = () => {
  const [state, setState] = useState({ menuOpen: false, pathname: '' });
  const isActive = state.menuOpen ? ' is-active' : '';
  useEffect(() => componentDidMount(setState), []);
  return (
    <nav className="navbar" role="navigation" aria-label="main navigation">
      <div className="navbar-brand">
        <Link className="navbar-item" to="/" aria-label="Home page">
          <img src={logo} alt="logo" style={{ height: 28 }} />
        </Link>
        <button
          className={`button is-white navbar-burger burger${isActive}`}
          aria-label="menu"
          aria-expanded="false"
          onClick={() => onClick(state, setState)}
        >
          <span aria-hidden="true" />
          <span aria-hidden="true" />
          <span aria-hidden="true" />
        </button>
      </div>
      <div className={`navbar-menu${isActive}`}>
        <div className="navbar-start">
          <Link
            className={`navbar-item is-tab${
              state.pathname === '/' ? ' is-active' : ''
            }`}
            to="/"
            aria-label="Home page"
          >
            Home
          </Link>
          <Link
            className={`navbar-item is-tab${
              state.pathname.startsWith('/data') ? ' is-active' : ''
            }`}
            to="/data"
            aria-label="Data"
          >
            Data
          </Link>
          <Link
            className={`navbar-item is-tab${
              state.pathname.startsWith('/maps') ? ' is-active' : ''
            }`}
            to="/maps"
            aria-label="Maps"
          >
            Maps
          </Link>
        </div>
        <div className="navbar-end">
          <div className="navbar-item">
            <div className="buttons"></div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default PageHeader;

import React from 'react';

import Header from './header';

const Layout = ({ children }) => {
  return (
    <>
      <Header />
      <section className="section">
        <div className="container">
          <main>{children}</main>
        </div>
      </section>
      <footer className="footer">
        <div className="content has-text-centered">
          <p>
            © {new Date().getFullYear()},{' '}
            <a href="https://github.com/fieldmaps">Max Malynowsky</a>
          </p>
        </div>
      </footer>
    </>
  );
};

export default Layout;

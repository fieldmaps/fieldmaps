import React from 'react';

export default () => (
  <footer className="footer">
    <div className="content has-text-centered">
      <p>
        © {new Date().getFullYear()}{' '}
        <a href="https://github.com/fieldmaps">Max Malynowsky</a>
      </p>
    </div>
  </footer>
);

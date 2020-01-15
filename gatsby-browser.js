import { navigate } from 'gatsby';

import './src/styles/styles.sass';

export const onServiceWorkerUpdateReady = () => {
  navigate(window.location.pathname);
};

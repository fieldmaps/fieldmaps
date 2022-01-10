import React from 'react';
import Metadata from '../components/common/metadata';
import Header from '../components/common/header';
import Body from '../components/common/body';
import Footer from '../components/common/footer';
import Content from '../components/content/404';

export default () => (
  <>
    <Metadata page="404" />
    <Header active="" />
    <Body>
      <Content />
    </Body>
    <Footer />
  </>
);

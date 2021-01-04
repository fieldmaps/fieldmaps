import React from 'react';
import Metadata from '../components/common/metadata';
import Header from '../components/common/header';
import Body from '../components/common/body';
import Footer from '../components/common/footer';
import Content from '../components/content/about';

export default () => (
  <>
    <Metadata page="About" />
    <Header active="about" />
    <Body>
      <Content />
    </Body>
    <Footer />
  </>
);

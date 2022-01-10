import React from 'react';
import Metadata from '../../components/common/metadata';
import Header from '../../components/common/header';
import HeaderData from '../../components/common/header-data';
import Body from '../../components/common/body';
import Footer from '../../components/common/footer';
import Content from '../../components/content/data-geoboundaries';

export default () => (
  <>
    <Metadata page="Data" />
    <Header active="data" />
    <HeaderData active="geoboundaries" />
    <Body>
      <Content />
    </Body>
    <Footer />
  </>
);

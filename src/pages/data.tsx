import React from 'react';
import { Link } from 'gatsby';

import Layout from '../components/layout';
import SEO from '../components/seo';

import cods from '../images/cods.svg';
import settlements from '../images/settlements.png';
import roads from '../images/roads.jpg';
import lakes from '../images/lakes.png';
import rivers from '../images/rivers.jpg';
import parks from '../images/parks.jpg';
import wash from '../images/wash.png';
import hospital from '../images/hospital.png';
import school from '../images/school.jpg';

const sources = [
  {
    img: cods,
    link: '/data/cods',
    title: 'Administrative Boundaries',
    subtitle: '',
    description:
      "Common Operational Datasets (CODs) are authoritative reference datasets needed to support operations and decision-making for all actors in a humanitarian response. CODs are 'best available' datasets that ensure consistency and simplify the discovery and exchange of key data. Core CODs are required in all disaster-prone countries as a preparedness measure",
  },
  {
    img: settlements,
    link: '/data',
    title: 'Settlements',
    subtitle: '(coming soon)',
    description: 'Description',
  },
  {
    img: roads,
    link: '/data',
    title: 'Roads',
    subtitle: '(coming soon)',
    description: 'Description',
  },
  {
    img: rivers,
    link: '/data',
    title: 'Rivers',
    subtitle: '(coming soon)',
    description: 'Description',
  },
  {
    img: lakes,
    link: '/data',
    title: 'Lakes, Marshes, Wetlands',
    subtitle: '(coming soon)',
    description: 'Description',
  },
  {
    img: parks,
    link: '/data',
    title: 'Parks and Protected Areas',
    subtitle: '(coming soon)',
    description: 'Description',
  },
  {
    img: wash,
    link: '/data',
    title: 'Water Sanitation & Hygiene Infrastructure',
    subtitle: '(coming soon)',
    description: 'Description',
  },
  {
    img: hospital,
    link: '/data',
    title: 'Health Facilities',
    subtitle: '(coming soon)',
    description: 'Description',
  },
  {
    img: school,
    link: '/data',
    title: 'Education Facilities',
    subtitle: '(coming soon)',
    description: 'Description',
  },
];

const SecondPage = () => (
  <Layout>
    <SEO title="Data" />
    {sources.map(({ img, link, title, subtitle, description }, index) => (
      <div className="box" key={index}>
        <article className="media">
          <Link to={link}>
            <figure className="media-left">
              <p className="image is-128x128">
                <img src={img} alt="" />
              </p>
            </figure>
          </Link>
          <div className="media-content">
            <div className="content">
              <p>
                <strong>{title}</strong> <small>{subtitle}</small>
                <br />
                {description}
              </p>
            </div>
          </div>
        </article>
      </div>
    ))}
  </Layout>
);

export default SecondPage;

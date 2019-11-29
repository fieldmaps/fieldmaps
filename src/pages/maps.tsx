import React from 'react';
import { graphql } from 'gatsby';
import Img from 'gatsby-image';

import Layout from '../components/layout';
import SEO from '../components/seo';

const maps = [
  ['South Sudan', 'ssd'],
  ['Nigeria', 'nga'],
  ['Sudan', 'sdn'],
  ['Democratic Republic of the Congo', 'cod'],
  ['Central African Republic', 'caf'],
  ['Ethiopia', 'eth'],
  ['Kenya', 'ken'],
  ['Uganda', 'uga'],
];

const getImage = (images: any, name: string) =>
  images.find(image => image.node.fluid.originalName === name + '.png');

interface Props {
  data: {
    allImageSharp: {
      edges: {
        node: {
          fluid: {
            src: string;
          };
        };
      };
    };
  };
}

const MapsPage = ({ data: { allImageSharp } }: Props) => (
  <Layout>
    <SEO title="Maps" />
    <nav className="columns is-multiline">
      {maps.map(([name, code], index) => (
        <div
          className="column is-one-quarter"
          style={{ display: 'flex' }}
          key={index}
        >
          <div className="card">
            <a
              className="card-image"
              href={`https://${code}-atlas.fieldmaps.io`}
            >
              <Img
                fluid={{
                  ...getImage(allImageSharp.edges, code).node.fluid,
                  aspectRatio: 4 / 3,
                }}
                alt="Placeholder image"
              />
            </a>
            <div className="card-content">
              <div className="media">
                <div className="media-content">
                  <p className="title is-4">
                    <a href={`https://${code}-atlas.fieldmaps.io`}>{name}</a>
                  </p>
                </div>
              </div>
              <div className="content">
                Reference atlas for {code.toUpperCase()} settlement data, with
                built-in search. This map is a work in progress, with
                improvements planned for the future.
              </div>
            </div>
          </div>
        </div>
      ))}
    </nav>
  </Layout>
);

export const query = graphql`
  query {
    allImageSharp {
      edges {
        node {
          fluid {
            sizes
            src
            aspectRatio
            originalName
            srcSet
          }
        }
      }
    }
  }
`;

export default MapsPage;

import React from 'react';

interface Props {
  htmlAttributes: any;
  headComponents: any[];
  bodyAttributes: any;
  preBodyComponents: any[];
  body: string;
  postBodyComponents: any[];
}

const HTML = (props: Props) => {
  let headComponents = props.headComponents;
  let css;
  if (process.env.NODE_ENV === 'production') {
    const { props } = headComponents.find(e => e.type === 'style');
    css = <link rel="stylesheet" href={props['data-href']} />;
    headComponents = headComponents.filter(e => e.type !== 'style');
  }
  return (
    <html {...props.htmlAttributes}>
      <head>
        <meta charSet="utf-8" />
        <meta httpEquiv="x-ua-compatible" content="ie=edge" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, shrink-to-fit=no"
        />
        {css}
        {headComponents}
      </head>
      <body {...props.bodyAttributes}>
        {props.preBodyComponents}
        <noscript key="noscript" id="gatsby-noscript">
          This app works best with JavaScript enabled.
        </noscript>
        <div
          key={`body`}
          id="___gatsby"
          dangerouslySetInnerHTML={{ __html: props.body }}
        />
        {props.postBodyComponents}
      </body>
    </html>
  );
};

export default HTML;

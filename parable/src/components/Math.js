import React from "react";
import katex from "katex";

export const InlineMath = ({ math }) => {
  const html = katex.renderToString(math, {
    throwOnError: false,
    displayMode: false,
  });
  return <span dangerouslySetInnerHTML={{ __html: html }} />;
};

export const BlockMath = ({ math }) => {
  const html = katex.renderToString(math, {
    throwOnError: false,
    displayMode: true,
  });
  return (
    <div className="equation-block" dangerouslySetInnerHTML={{ __html: html }} />
  );
};

/**
 * Shared D3 scaffolding for the cardiac panels.
 *
 * Charts here render measured data. Where a series exists to show that a claim
 * *fails* — a forced construction, an estimate within noise of zero — it is
 * labelled as such rather than drawn as though it were a result.
 */

import * as d3 from "d3";
import { useEffect, useRef } from "react";

import { palette } from "../../theme";

export interface Margin {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

export const M: Margin = { top: 18, right: 14, bottom: 30, left: 44 };

/** Sleep-stage colours, used consistently across every cardiac chart. */
export const STAGE_COLOUR: Record<string, string> = {
  deep: "#2c4a7c",
  light: "#4a9fd8",
  rem: "#8b6cc8",
  awake: "#e8a838",
};

export const STAGE_ORDER = ["deep", "light", "rem", "awake"] as const;

/**
 * Mount a D3 render into an SVG, re-running when dependencies change.
 *
 * The callback receives a cleared root group already offset by the margin, so
 * every chart shares one coordinate convention.
 */
export function useD3(
  render: (g: d3.Selection<SVGGElement, unknown, null, undefined>, w: number, h: number) => void,
  width: number,
  height: number,
  deps: unknown[],
) {
  const ref = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();
    const w = width - M.left - M.right;
    const h = height - M.top - M.bottom;
    const g = svg.append("g").attr("transform", `translate(${M.left},${M.top})`);
    render(g, w, h);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [width, height, ...deps]);

  return ref;
}

/** Axes in the panel's idiom: dim ticks, faint gridlines, no chrome. */
export function axes(
  g: d3.Selection<SVGGElement, unknown, null, undefined>,
  x: d3.AxisScale<never> | d3.ScaleLinear<number, number> | d3.ScaleBand<string>,
  y: d3.ScaleLinear<number, number>,
  w: number,
  h: number,
  opts: { xTicks?: number; yTicks?: number; xFormat?: (d: never) => string } = {},
) {
  const xAxis = d3.axisBottom(x as d3.AxisScale<d3.AxisDomain>).ticks(opts.xTicks ?? 5);
  if (opts.xFormat) xAxis.tickFormat(opts.xFormat as never);

  g.append("g")
    .attr("transform", `translate(0,${h})`)
    .call(xAxis as never)
    .call((s) => s.selectAll("text").attr("fill", palette.textDim).style("font-size", "9px"))
    .call((s) => s.selectAll("line").attr("stroke", palette.borderSubtle))
    .call((s) => s.select(".domain").attr("stroke", palette.border));

  g.append("g")
    .call(d3.axisLeft(y).ticks(opts.yTicks ?? 4).tickSize(-w))
    .call((s) => s.selectAll("text").attr("fill", palette.textDim).style("font-size", "9px"))
    .call((s) => s.selectAll("line").attr("stroke", palette.borderSubtle))
    .call((s) => s.select(".domain").attr("stroke", palette.border));
}

/** A short caption under a chart. Used for the caveats, not decoration. */
export function caption(
  g: d3.Selection<SVGGElement, unknown, null, undefined>,
  h: number,
  text: string,
  colour: string = palette.textFaint,
) {
  g.append("text")
    .attr("x", 0)
    .attr("y", h + 26)
    .attr("fill", colour)
    .style("font-size", "9px")
    .text(text);
}

export function svgProps(width: number, height: number) {
  return { width, height, style: { display: "block" as const } };
}

/**
 * Stage transitions as typed events, and whether they discriminate.
 *
 * Twelve transition types across 2,856 events look like ample material for a
 * law comparison. They are not: η = 0.0496 on this record, below the flagging
 * threshold, so the type means do not separate and no comparison built on
 * them can adjudicate the typing.
 *
 * The chart therefore leads with η rather than with the per-type means. Drawn
 * the other way round — twelve tidy bars, the statistic in a footnote — it
 * would invite exactly the inference the diagnostic exists to prevent.
 */

import * as d3 from "d3";

import { mono, palette } from "../../theme";
import { M, axes, caption, useD3 } from "./d3util";

export interface TransitionType {
  type: string;
  mean: number;
  sd: number;
  n: number;
  values: number[];
}

interface Props {
  types: TransitionType[];
  eta: number;
  between: number;
  within: number;
  threshold: number;
  informative: boolean;
  width?: number;
  height?: number;
}

export function CardiacTransitions({
  types,
  eta,
  between,
  within,
  threshold,
  informative,
  width = 376,
  height = 280,
}: Props) {
  const ref = useD3(
    (g, w, h) => {
      const sorted = [...types].sort((a, b) => b.mean - a.mean);
      const y = d3
        .scaleBand<string>()
        .domain(sorted.map((t) => t.type))
        .range([0, h])
        .padding(0.25);

      const spread = d3.max(sorted, (t) => Math.abs(t.mean) + t.sd) ?? 0.1;
      const x = d3.scaleLinear().domain([-spread * 1.1, spread * 1.1]).range([0, w]);

      axes(g, x, d3.scaleLinear().domain([0, 1]).range([h, 0]), w, h, { xTicks: 5, yTicks: 0 });

      g.append("g")
        .call(d3.axisLeft(y).tickSize(0))
        .call((s) =>
          s
            .selectAll("text")
            .attr("fill", palette.textDim)
            .style("font-family", mono)
            .style("font-size", "8px"),
        )
        .call((s) => s.select(".domain").remove());

      // zero line: a negative mean is an event that widened the gap
      g.append("line")
        .attr("x1", x(0))
        .attr("x2", x(0))
        .attr("y1", 0)
        .attr("y2", h)
        .attr("stroke", palette.textFaint);

      // ±1 sd, drawn because the within-type spread is the whole point:
      // the bars overlap, which is what a low η looks like
      g.selectAll("line.sd")
        .data(sorted)
        .join("line")
        .attr("class", "sd")
        .attr("x1", (t) => x(t.mean - t.sd))
        .attr("x2", (t) => x(t.mean + t.sd))
        .attr("y1", (t) => (y(t.type) ?? 0) + y.bandwidth() / 2)
        .attr("y2", (t) => (y(t.type) ?? 0) + y.bandwidth() / 2)
        .attr("stroke", informative ? palette.evidential : palette.identity)
        .attr("stroke-width", y.bandwidth() * 0.55)
        .attr("opacity", 0.28);

      g.selectAll("circle.m")
        .data(sorted)
        .join("circle")
        .attr("class", "m")
        .attr("cx", (t) => x(t.mean))
        .attr("cy", (t) => (y(t.type) ?? 0) + y.bandwidth() / 2)
        .attr("r", 3)
        .attr("fill", (t) =>
          informative ? (t.mean >= 0 ? palette.resolved : palette.failed) : palette.identity,
        );

      g.append("text")
        .attr("x", w)
        .attr("y", -6)
        .attr("text-anchor", "end")
        .attr("fill", palette.textDim)
        .style("font-size", "9px")
        .text(`mean κ per transition type ±1 sd · ${d3.sum(types, (t) => t.n)} events`);

      caption(
        g,
        h,
        informative
          ? "type means separate; a law comparison can adjudicate the typing"
          : "bars overlap: the type means do not separate",
        informative ? palette.textDim : palette.identity,
      );
    },
    width,
    height,
    [types, informative],
  );

  return (
    <div style={{ width }}>
      <EtaBanner
        eta={eta}
        between={between}
        within={within}
        threshold={threshold}
        informative={informative}
        width={width}
      />
      <svg ref={ref} width={width} height={height} />
    </div>
  );
}

/**
 * η, stated before the per-type means rather than after them.
 *
 * Below the threshold the banner says what a reader would otherwise infer
 * wrongly: that a non-trivial correlation on this substrate would be carried
 * by something other than type identity.
 */
function EtaBanner({
  eta,
  between,
  within,
  threshold,
  informative,
  width,
}: {
  eta: number;
  between: number;
  within: number;
  threshold: number;
  informative: boolean;
  width: number;
}) {
  const barW = width - 20;
  // sqrt scale: η is small here and a linear axis would hide the margin
  const pos = Math.sqrt(Math.max(eta, 0)) * barW;
  const mark = Math.sqrt(threshold) * barW;
  const colour = informative ? palette.resolved : palette.failed;

  return (
    <div style={{ fontFamily: mono, fontSize: 11, marginBottom: 6 }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <span style={{ color: palette.textDim }}>type separation η</span>
        <span style={{ color: colour, fontWeight: 600 }}>{eta.toFixed(4)}</span>
      </div>

      <svg width={barW} height={16} style={{ display: "block", marginTop: 3 }}>
        <rect width={barW} height={8} rx={2} fill={palette.bgSunken} />
        <rect width={mark} height={8} fill={palette.failed} opacity={0.16} />
        <rect width={Math.max(pos, 2)} height={8} rx={2} fill={colour} />
        <line x1={mark} x2={mark} y1={-1} y2={9} stroke={palette.failed} strokeDasharray="2,2" />
      </svg>

      <div style={{ color: palette.textFaint, fontSize: 9, marginTop: 2 }}>
        between {between.toExponential(1)} · within {within.toExponential(1)} · threshold{" "}
        {threshold}
      </div>

      {!informative && (
        <div
          style={{
            marginTop: 6,
            padding: "6px 8px",
            borderLeft: `2px solid ${palette.failed}`,
            background: palette.bgSunken,
            fontSize: 10,
            lineHeight: 1.5,
            color: palette.textDim,
          }}
        >
          Below the flagging threshold. The transition types do not
          discriminate, so a law comparison on this substrate cannot adjudicate
          the typing. A non-trivial correlation may still appear and would be
          carried by cascade length, not by type identity — it is{" "}
          <strong>not</strong> evidence that the typing is correct.
        </div>
      )}
    </div>
  );
}

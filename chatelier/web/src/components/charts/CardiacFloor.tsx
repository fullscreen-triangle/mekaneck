/**
 * The floor test on the 86-night record.
 *
 * This is the chart the cardiac module exists to produce, and it reports a
 * negative result: separation cost has no positive floor at either resolution
 * tested. The design problem is that a negative result is easy to render as
 * though it were a positive one, so three things are made explicit —
 *
 * - the fitted intercept is drawn against the axis at 1/n = 0, where a floor
 *   would appear as a positive y-intercept and does not;
 * - the sample minimum is drawn alongside it, since it is always ≥ 0 and its
 *   positivity would be no evidence either way;
 * - the region at or below zero is shaded, because entering it is the only
 *   observation that can falsify a positivity claim.
 */

import * as d3 from "d3";

import { palette, mono } from "../../theme";
import { M, axes, caption, useD3 } from "./d3util";

export interface FloorCurve {
  points: { n: number; inv_n: number; min: number }[];
  slope: number;
  intercept: number;
  sample_minimum: number;
}

interface Props {
  curve: FloorCurve;
  label: string;
  resolution: string;
  exactlyZero: number;
  n: number;
  width?: number;
  height?: number;
}

export function CardiacFloor({
  curve,
  label,
  resolution,
  exactlyZero,
  n,
  width = 376,
  height = 210,
}: Props) {
  const ref = useD3(
    (g, w, h) => {
      const pts = curve.points;
      const xMax = d3.max(pts, (p) => p.inv_n) ?? 1;
      const x = d3.scaleLinear().domain([0, xMax * 1.05]).range([0, w]);

      const yVals = pts.map((p) => p.min).concat([curve.intercept, 0]);
      const yMin = Math.min(...yVals);
      const yMax = Math.max(...yVals);
      const pad = (yMax - yMin) * 0.15 || 1;
      const y = d3.scaleLinear().domain([yMin - pad, yMax + pad]).range([h, 0]);

      // The falsifying region. Only an estimate that enters it contradicts a
      // positive floor, so it is drawn rather than left implicit.
      if (y.domain()[0] < 0) {
        g.append("rect")
          .attr("x", 0)
          .attr("y", y(0))
          .attr("width", w)
          .attr("height", h - y(0))
          .attr("fill", palette.failed)
          .attr("opacity", 0.1);
        g.append("line")
          .attr("x1", 0)
          .attr("x2", w)
          .attr("y1", y(0))
          .attr("y2", y(0))
          .attr("stroke", palette.failed)
          .attr("stroke-dasharray", "3,3");
      }

      axes(g, x, y, w, h, { xTicks: 4, yTicks: 4 });

      // fitted line, extrapolated to the intercept
      g.append("line")
        .attr("x1", x(0))
        .attr("x2", x(xMax))
        .attr("y1", y(curve.intercept))
        .attr("y2", y(curve.intercept + curve.slope * xMax))
        .attr("stroke", palette.evidential)
        .attr("stroke-width", 1.4);

      g.selectAll("circle.pt")
        .data(pts)
        .join("circle")
        .attr("class", "pt")
        .attr("cx", (p) => x(p.inv_n))
        .attr("cy", (p) => y(p.min))
        .attr("r", 2.6)
        .attr("fill", palette.evidential)
        .attr("opacity", 0.75);

      // the intercept: where a positive floor would show itself
      const supports = curve.intercept > 1e-3;
      g.append("circle")
        .attr("cx", x(0))
        .attr("cy", y(curve.intercept))
        .attr("r", 5)
        .attr("fill", supports ? palette.resolved : palette.failed)
        .attr("stroke", palette.bg)
        .attr("stroke-width", 1.5);

      g.append("text")
        .attr("x", x(0) + 9)
        .attr("y", y(curve.intercept) + 3)
        .attr("fill", supports ? palette.resolved : palette.failed)
        .style("font-family", mono)
        .style("font-size", "10px")
        .text(`β̂ = ${curve.intercept.toFixed(3)}`);

      g.append("text")
        .attr("x", w)
        .attr("y", -6)
        .attr("text-anchor", "end")
        .attr("fill", palette.textDim)
        .style("font-size", "9px")
        .text(`${label} · ${resolution} · n=${n.toLocaleString()}`);

      g.append("text")
        .attr("x", -M.left + 4)
        .attr("y", -6)
        .attr("fill", palette.textFaint)
        .style("font-size", "9px")
        .text("min S");

      caption(
        g,
        h,
        exactlyZero > 0
          ? `${exactlyZero.toLocaleString()} separations are exactly zero — the estimator could have returned a positive floor and did not.`
          : "zero was never attained in this sample",
        exactlyZero > 0 ? palette.textDim : palette.warn,
      );
    },
    width,
    height,
    [curve, exactlyZero, n],
  );

  return <svg ref={ref} width={width} height={height} />;
}

/**
 * The forced constructions, shown so they can be discounted.
 *
 * An affine offset `S = scale − rmssd` returns a positive intercept for every
 * scale above the maximum. Plotting the intercept against the scale makes the
 * dependence visible: the "floor" tracks the constant, not the physiology.
 */
export function ForcedConstruction({
  points,
  rmssdMax,
  width = 376,
  height = 180,
}: {
  points: { scale: number; intercept: number }[];
  rmssdMax: number;
  width?: number;
  height?: number;
}) {
  const ref = useD3(
    (g, w, h) => {
      const x = d3
        .scaleLinear()
        .domain([0, (d3.max(points, (p) => p.scale) ?? 1) * 1.05])
        .range([0, w]);
      const y = d3
        .scaleLinear()
        .domain([0, (d3.max(points, (p) => p.intercept) ?? 1) * 1.1])
        .range([h, 0]);

      axes(g, x, y, w, h, { xTicks: 4, yTicks: 4 });

      // the identity the artefact follows: intercept ≈ scale − constant
      g.append("line")
        .attr("x1", x(rmssdMax))
        .attr("x2", x(x.domain()[1]))
        .attr("y1", y(0))
        .attr("y2", y(x.domain()[1] - rmssdMax))
        .attr("stroke", palette.identity)
        .attr("stroke-dasharray", "4,3");

      g.append("path")
        .datum(points)
        .attr("fill", "none")
        .attr("stroke", palette.identity)
        .attr("stroke-width", 1.6)
        .attr(
          "d",
          d3
            .line<{ scale: number; intercept: number }>()
            .x((p) => x(p.scale))
            .y((p) => y(p.intercept)) as never,
        );

      g.selectAll("circle.f")
        .data(points)
        .join("circle")
        .attr("class", "f")
        .attr("cx", (p) => x(p.scale))
        .attr("cy", (p) => y(p.intercept))
        .attr("r", 3.2)
        .attr("fill", palette.identity);

      g.append("text")
        .attr("x", w)
        .attr("y", -6)
        .attr("text-anchor", "end")
        .attr("fill", palette.identity)
        .style("font-size", "9px")
        .text("NOT EVIDENCE — positivity by construction");

      caption(
        g,
        h,
        `The intercept tracks the chosen scale, offset by ~${rmssdMax.toFixed(0)} ms. Any scale above the maximum yields a positive floor.`,
        palette.identity,
      );
    },
    width,
    height,
    [points, rmssdMax],
  );

  return <svg ref={ref} width={width} height={height} />;
}

/**
 * Distribution of consecutive rate differences at 5-second resolution.
 *
 * The mass at zero and the spike at 1 bpm are the finding: heart rate is
 * reported as an integer, so the measured floor is the instrument quantum and
 * no separation below 1 bpm is representable at all.
 */
export function QuantumHistogram({
  histogram,
  zeroFraction,
  width = 376,
  height = 190,
}: {
  histogram: { bpm: number; count: number }[];
  zeroFraction: number;
  width?: number;
  height?: number;
}) {
  const ref = useD3(
    (g, w, h) => {
      const x = d3
        .scaleBand<string>()
        .domain(histogram.map((d) => String(d.bpm)))
        .range([0, w])
        .padding(0.18);
      const y = d3
        .scaleLinear()
        .domain([0, (d3.max(histogram, (d) => d.count) ?? 1) * 1.08])
        .range([h, 0]);

      axes(g, x, y, w, h, { yTicks: 4 });

      g.selectAll("rect.b")
        .data(histogram)
        .join("rect")
        .attr("class", "b")
        .attr("x", (d) => x(String(d.bpm)) ?? 0)
        .attr("y", (d) => y(d.count))
        .attr("width", x.bandwidth())
        .attr("height", (d) => h - y(d.count))
        .attr("rx", 1)
        // 0 and 1 bpm are the quantisation story; the rest is physiology
        .attr("fill", (d) => (d.bpm <= 1 ? palette.warn : palette.evidential))
        .attr("opacity", (d) => (d.bpm <= 1 ? 0.95 : 0.7));

      g.append("text")
        .attr("x", w)
        .attr("y", -6)
        .attr("text-anchor", "end")
        .attr("fill", palette.textDim)
        .style("font-size", "9px")
        .text("|ΔHR| between consecutive 5 s epochs (bpm)");

      caption(
        g,
        h,
        `${(zeroFraction * 100).toFixed(1)}% are exactly zero: the sensor reported the same integer twice. Below 1 bpm no separation is representable.`,
        palette.warn,
      );
    },
    width,
    height,
    [histogram, zeroFraction],
  );

  return <svg ref={ref} width={width} height={height} />;
}

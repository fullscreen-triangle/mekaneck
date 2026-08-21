/**
 * Within-night structure: the hypnogram, and the cardiac series against it.
 *
 * These are descriptive rather than inferential, and are drawn because the
 * floor and separation results are otherwise uninterpretable — a reader
 * needs to see that the record contains real sleep architecture before being
 * told what could not be inferred from it.
 */

import * as d3 from "d3";

import { mono, palette } from "../../theme";
import { M, STAGE_COLOUR, STAGE_ORDER, axes, caption, useD3 } from "./d3util";

export interface StageRun {
  stage: string;
  from: number;
  to: number;
}

export interface TracePoint {
  t: number;
  rmssd: number;
  hr: number | null;
  stage?: string;
}

/** The hypnogram as a stage ribbon: what the night actually did. */
export function Hypnogram({
  runs,
  night,
  width = 376,
  height = 74,
}: {
  runs: StageRun[];
  night: number;
  width?: number;
  height?: number;
}) {
  const ref = useD3(
    (g, w, h) => {
      const end = d3.max(runs, (r) => r.to) ?? 1;
      const x = d3.scaleLinear().domain([0, end]).range([0, w]);
      const lane = d3
        .scaleBand<string>()
        .domain([...STAGE_ORDER])
        .range([0, h])
        .padding(0.22);

      g.selectAll("rect.r")
        .data(runs)
        .join("rect")
        .attr("class", "r")
        .attr("x", (r) => x(r.from))
        .attr("width", (r) => Math.max(x(r.to) - x(r.from), 1))
        .attr("y", (r) => lane(r.stage) ?? 0)
        .attr("height", lane.bandwidth())
        .attr("rx", 1)
        .attr("fill", (r) => STAGE_COLOUR[r.stage] ?? palette.textFaint);

      g.append("g")
        .call(d3.axisLeft(lane).tickSize(0))
        .call((s) => s.selectAll("text").attr("fill", palette.textDim).style("font-size", "8px"))
        .call((s) => s.select(".domain").remove());

      g.append("g")
        .attr("transform", `translate(0,${h})`)
        .call(d3.axisBottom(x).ticks(5).tickFormat((d) => `${Number(d) / 60}h`))
        .call((s) => s.selectAll("text").attr("fill", palette.textDim).style("font-size", "8px"))
        .call((s) => s.select(".domain").attr("stroke", palette.border))
        .call((s) => s.selectAll("line").attr("stroke", palette.borderSubtle));

      g.append("text")
        .attr("x", w)
        .attr("y", -5)
        .attr("text-anchor", "end")
        .attr("fill", palette.textFaint)
        .style("font-family", mono)
        .style("font-size", "9px")
        .text(`night ${night}`);
    },
    width,
    height,
    [runs, night],
  );

  return <svg ref={ref} width={width} height={height} />;
}

/**
 * RMSSD and heart rate through one night, coloured by stage.
 *
 * The two series are on independent axes because they are different
 * quantities; the shared x is time from sleep onset.
 */
export function NightTrace({
  points,
  night,
  width = 376,
  height = 200,
}: {
  points: TracePoint[];
  night: number;
  width?: number;
  height?: number;
}) {
  const ref = useD3(
    (g, w, h) => {
      if (points.length === 0) return;
      const x = d3
        .scaleLinear()
        .domain(d3.extent(points, (p) => p.t) as [number, number])
        .range([0, w]);
      const yR = d3
        .scaleLinear()
        .domain([0, (d3.max(points, (p) => p.rmssd) ?? 1) * 1.1])
        .range([h, 0]);
      const hrs = points.map((p) => p.hr).filter((v): v is number => v != null);
      const yH = d3
        .scaleLinear()
        .domain([(d3.min(hrs) ?? 40) - 3, (d3.max(hrs) ?? 90) + 3])
        .range([h, 0]);

      axes(g, x, yR, w, h, { xTicks: 5, yTicks: 4 });

      // stage bands behind the series, so a reader can attribute excursions
      let runStart = 0;
      for (let i = 1; i <= points.length; i += 1) {
        const changed = i === points.length || points[i].stage !== points[runStart].stage;
        if (changed) {
          const s = points[runStart].stage;
          if (s) {
            g.append("rect")
              .attr("x", x(points[runStart].t))
              .attr("width", Math.max(x(points[i - 1].t) - x(points[runStart].t), 1))
              .attr("y", 0)
              .attr("height", h)
              .attr("fill", STAGE_COLOUR[s])
              .attr("opacity", 0.1);
          }
          runStart = i;
        }
      }

      g.append("path")
        .datum(points)
        .attr("fill", "none")
        .attr("stroke", palette.evidential)
        .attr("stroke-width", 1.3)
        .attr(
          "d",
          d3
            .line<TracePoint>()
            .x((p) => x(p.t))
            .y((p) => yR(p.rmssd))
            .curve(d3.curveMonotoneX) as never,
        );

      g.append("path")
        .datum(points.filter((p) => p.hr != null))
        .attr("fill", "none")
        .attr("stroke", palette.contested)
        .attr("stroke-width", 1.1)
        .attr("opacity", 0.85)
        .attr(
          "d",
          d3
            .line<TracePoint>()
            .x((p) => x(p.t))
            .y((p) => yH(p.hr as number))
            .curve(d3.curveMonotoneX) as never,
        );

      g.append("g")
        .attr("transform", `translate(${w},0)`)
        .call(d3.axisRight(yH).ticks(4))
        .call((s) => s.selectAll("text").attr("fill", palette.contested).style("font-size", "8px"))
        .call((s) => s.selectAll("line").attr("stroke", palette.borderSubtle))
        .call((s) => s.select(".domain").attr("stroke", palette.border));

      g.append("text")
        .attr("x", -M.left + 4)
        .attr("y", -6)
        .attr("fill", palette.evidential)
        .style("font-size", "9px")
        .text("RMSSD ms");

      g.append("text")
        .attr("x", w)
        .attr("y", -6)
        .attr("text-anchor", "end")
        .attr("fill", palette.contested)
        .style("font-size", "9px")
        .text(`bpm · night ${night}`);

      caption(g, h, "minutes from sleep onset; bands are stages");
    },
    width,
    height,
    [points, night],
  );

  return <svg ref={ref} width={width} height={height} />;
}

/** Per-night summary: RMSSD against sleep efficiency, sized by duration. */
export function NightScatter({
  nights,
  width = 376,
  height = 210,
}: {
  nights: {
    night: number;
    rmssd: number | null;
    efficiency: number | null;
    duration_h: number | null;
    deep_h: number | null;
  }[];
  width?: number;
  height?: number;
}) {
  const ref = useD3(
    (g, w, h) => {
      const pts = nights.filter(
        (n) => n.rmssd != null && n.efficiency != null && n.duration_h != null,
      );
      if (pts.length === 0) return;

      const x = d3
        .scaleLinear()
        .domain(d3.extent(pts, (p) => p.efficiency as number) as [number, number])
        .nice()
        .range([0, w]);
      const y = d3
        .scaleLinear()
        .domain([0, (d3.max(pts, (p) => p.rmssd as number) ?? 1) * 1.1])
        .range([h, 0]);
      const r = d3
        .scaleSqrt()
        .domain(d3.extent(pts, (p) => p.duration_h as number) as [number, number])
        .range([2, 6]);
      const colour = d3
        .scaleSequential(d3.interpolateViridis)
        .domain(d3.extent(pts, (p) => p.deep_h ?? 0) as [number, number]);

      axes(g, x, y, w, h, { xTicks: 5, yTicks: 4 });

      g.selectAll("circle.n")
        .data(pts)
        .join("circle")
        .attr("class", "n")
        .attr("cx", (p) => x(p.efficiency as number))
        .attr("cy", (p) => y(p.rmssd as number))
        .attr("r", (p) => r(p.duration_h as number))
        .attr("fill", (p) => colour(p.deep_h ?? 0))
        .attr("opacity", 0.8);

      g.append("text")
        .attr("x", w)
        .attr("y", -6)
        .attr("text-anchor", "end")
        .attr("fill", palette.textDim)
        .style("font-size", "9px")
        .text(`${pts.length} nights · size = duration, colour = deep sleep`);

      g.append("text")
        .attr("x", -M.left + 4)
        .attr("y", -6)
        .attr("fill", palette.textFaint)
        .style("font-size", "9px")
        .text("RMSSD ms");

      caption(g, h, "sleep efficiency (%)");
    },
    width,
    height,
    [nights],
  );

  return <svg ref={ref} width={width} height={height} />;
}

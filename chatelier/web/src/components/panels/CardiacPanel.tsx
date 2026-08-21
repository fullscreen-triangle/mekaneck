/**
 * The cardiac panel.
 *
 * Ordered so the caveats precede the results they qualify. A reader arriving
 * at the per-type means without having seen η, or at the floor plot without
 * having seen that two coordinate choices force their own answer, would draw
 * conclusions this record does not support.
 */

import { useEffect, useState } from "react";

import { mono, palette } from "../../theme";
import {
  CardiacFloor,
  ForcedConstruction,
  QuantumHistogram,
  type FloorCurve,
} from "../charts/CardiacFloor";
import { Hypnogram, NightScatter, NightTrace } from "../charts/CardiacNight";
import { CardiacTransitions, type TransitionType } from "../charts/CardiacTransitions";

interface ChartData {
  meta: { n_nights: number; n_epochs: number; source: string };
  per_night: {
    night: number;
    rmssd: number | null;
    efficiency: number | null;
    duration_h: number | null;
    deep_h: number | null;
  }[];
  traces: { night: number; points: { t: number; rmssd: number; hr: number | null; stage?: string }[] }[];
  hypnograms: { night: number; runs: { stage: string; from: number; to: number }[] }[];
  floor_test: {
    stage_level: { resolution: string; curve: FloorCurve; exactly_zero: number; n: number };
    intraday: {
      resolution: string;
      curve: FloorCurve;
      exactly_zero: number;
      zero_fraction: number;
      n: number;
      histogram: { bpm: number; count: number }[];
    };
    verdict: string;
  };
  forced_constructions: { affine: { scale: number; intercept: number }[]; rmssd_max: number };
  transitions: {
    types: TransitionType[];
    between: number;
    within: number;
    eta: number;
    informative: boolean;
    threshold: number;
  };
}

const SECTIONS = ["Finding", "Floor", "Nights", "Transitions"] as const;
type Section = (typeof SECTIONS)[number];

export function CardiacPanel({ width = 376 }: { width?: number }) {
  const [data, setData] = useState<ChartData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [section, setSection] = useState<Section>("Finding");
  const [nightIdx, setNightIdx] = useState(0);

  useEffect(() => {
    fetch("/dataset/cardiac_charts.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setData)
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) {
    return (
      <Note colour={palette.warn}>
        Chart data unavailable ({error}). Generate it with{" "}
        <code>python validation/build_cardiac_charts.py</code>.
      </Note>
    );
  }
  if (!data) {
    return <Note colour={palette.textFaint}>Loading record…</Note>;
  }

  const { floor_test, transitions, forced_constructions } = data;
  const trace = data.traces[nightIdx % data.traces.length];
  const hypno = data.hypnograms[nightIdx % data.hypnograms.length];

  return (
    <div style={{ width, fontFamily: mono, fontSize: 11 }}>
      <div style={{ display: "flex", gap: 2, marginBottom: 8 }}>
        {SECTIONS.map((s) => (
          <button
            key={s}
            onClick={() => setSection(s)}
            style={{
              flex: 1,
              padding: "3px 0",
              background: section === s ? palette.bgElevated : "transparent",
              border: `1px solid ${palette.border}`,
              borderRadius: 2,
              color: section === s ? palette.textBright : palette.textDim,
              fontFamily: mono,
              fontSize: 10,
              cursor: "pointer",
            }}
          >
            {s}
          </button>
        ))}
      </div>

      {section === "Finding" && (
        <>
          <Note colour={palette.failed}>
            <strong>No positive floor at either resolution tested.</strong> The
            measured floor is the instrument quantum: heart rate is reported as
            an integer, so no separation below 1 bpm is representable. A
            substrate over this record must declare a falsifiable estimator and
            expect it to fail, and a program requiring a positive floor will not
            type-check over it.
          </Note>
          <Note colour={palette.warn}>
            The claim rests on the <em>attained zeros</em>, not on the
            extrapolation. At 5 minutes the intercept is unstable — its sign
            flips with the ordering of the record and with the number of stages
            fitted, so it is reported with its spread and carries no claim on
            its own. At 5 seconds it is exactly zero with no spread, because
            quantisation puts it there.
          </Note>
          <Stat label="nights" value={data.meta.n_nights} />
          <Stat label="5-min epochs" value={data.meta.n_epochs.toLocaleString()} />
          <Stat
            label="stage separations"
            value={`${floor_test.stage_level.n} (${floor_test.stage_level.exactly_zero} exactly zero)`}
          />
          <Stat
            label="β̂ at 5 min"
            value={`${floor_test.stage_level.curve.intercept.toFixed(3)} ± ${floor_test.stage_level.curve.intercept_sd.toFixed(3)}`}
            colour={palette.warn}
          />
          <Stat
            label="β̂ at 5 s"
            value={floor_test.intraday.curve.intercept.toFixed(4)}
            colour={palette.failed}
          />
          <Stat
            label="η"
            value={`${transitions.eta.toFixed(4)} (below ${transitions.threshold})`}
            colour={palette.failed}
          />
        </>
      )}

      {section === "Floor" && (
        <>
          <CardiacFloor
            curve={floor_test.stage_level.curve}
            label="stage vs rest"
            resolution={floor_test.stage_level.resolution}
            exactlyZero={floor_test.stage_level.exactly_zero}
            n={floor_test.stage_level.n}
            width={width}
          />
          <CardiacFloor
            curve={floor_test.intraday.curve}
            label="consecutive epochs"
            resolution={floor_test.intraday.resolution}
            exactlyZero={floor_test.intraday.exactly_zero}
            n={floor_test.intraday.n}
            width={width}
          />
          <QuantumHistogram
            histogram={floor_test.intraday.histogram}
            zeroFraction={floor_test.intraday.zero_fraction}
            width={width}
          />
          <Divider label="discounted constructions" />
          <ForcedConstruction
            points={forced_constructions.affine}
            rmssdMax={forced_constructions.rmssd_max}
            width={width}
          />
        </>
      )}

      {section === "Nights" && (
        <>
          <div style={{ display: "flex", gap: 4, marginBottom: 6 }}>
            {data.traces.map((t, i) => (
              <button
                key={t.night}
                onClick={() => setNightIdx(i)}
                style={{
                  padding: "2px 7px",
                  background: i === nightIdx ? palette.evidential : "transparent",
                  border: `1px solid ${palette.border}`,
                  borderRadius: 2,
                  color: i === nightIdx ? palette.bg : palette.textDim,
                  fontFamily: mono,
                  fontSize: 9,
                  cursor: "pointer",
                }}
              >
                {t.night}
              </button>
            ))}
          </div>
          <Hypnogram runs={hypno.runs} night={hypno.night} width={width} />
          <NightTrace points={trace.points} night={trace.night} width={width} />
          <Divider label="all nights" />
          <NightScatter nights={data.per_night} width={width} />
        </>
      )}

      {section === "Transitions" && (
        <CardiacTransitions
          types={transitions.types}
          eta={transitions.eta}
          between={transitions.between}
          within={transitions.within}
          threshold={transitions.threshold}
          informative={transitions.informative}
          width={width}
        />
      )}
    </div>
  );
}

function Stat({
  label,
  value,
  colour = palette.text,
}: {
  label: string;
  value: string | number;
  colour?: string;
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        padding: "3px 4px",
        borderBottom: `1px solid ${palette.borderSubtle}`,
      }}
    >
      <span style={{ color: palette.textDim }}>{label}</span>
      <span style={{ color: colour }}>{value}</span>
    </div>
  );
}

function Note({ colour, children }: { colour: string; children: React.ReactNode }) {
  return (
    <div
      style={{
        padding: "7px 9px",
        marginBottom: 8,
        borderLeft: `2px solid ${colour}`,
        background: palette.bgSunken,
        fontSize: 10,
        lineHeight: 1.55,
        color: palette.textDim,
      }}
    >
      {children}
    </div>
  );
}

function Divider({ label }: { label: string }) {
  return (
    <div
      style={{
        margin: "12px 0 6px",
        fontSize: 9,
        color: palette.textFaint,
        textTransform: "uppercase",
        letterSpacing: "0.06em",
      }}
    >
      {label}
    </div>
  );
}

/**
 * Type separation η.
 *
 * η governs whether a law comparison can adjudicate the typing at all. Below
 * the flagging threshold the comparison is uninformative, and — this is the
 * part an interface usually gets wrong — a *non-trivial correlation can still
 * appear*, carried by cascade-length variation rather than by type identity.
 *
 * So the gauge does not merely colour a bar. When η is below threshold it
 * states that any correlation reported alongside it is not evidence that the
 * typing is correct, because that is the inference a reader would otherwise
 * draw from a healthy-looking r.
 */

import type { SeparationReport } from "../../connection/protocol";
import { UNINFORMATIVE_ETA, etaColour, mono, palette } from "../../theme";

interface Props {
  separation: SeparationReport | null;
  width?: number;
}

export function SeparationGauge({ separation, width = 360 }: Props) {
  if (!separation) {
    return (
      <div style={{ padding: 16, color: palette.textFaint, fontSize: 11, fontFamily: mono }}>
        No separation computed
      </div>
    );
  }

  const { eta, n_types, n_events, between, within, informative } = separation;
  const barW = width - 24;
  const colour = etaColour(eta);
  // η is often tiny; a linear axis would put every interesting value in one
  // pixel. A sqrt scale keeps the low end legible without misrepresenting order.
  const pos = Math.sqrt(Math.max(eta, 0)) * barW;

  return (
    <div style={{ width, fontFamily: mono, fontSize: 11, padding: "4px 0" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <span style={{ color: palette.textDim }}>Type separation η</span>
        <span style={{ color: colour, fontWeight: 600 }}>
          {eta < 1e-3 ? eta.toExponential(1) : eta.toFixed(3)}
        </span>
      </div>

      <svg width={barW} height={26}>
        <rect width={barW} height={10} rx={2} fill={palette.bgSunken} />
        <rect
          x={0}
          width={Math.sqrt(UNINFORMATIVE_ETA) * barW}
          height={10}
          fill={palette.failed}
          opacity={0.18}
        />
        <rect x={0} width={Math.max(pos, 2)} height={10} rx={2} fill={colour} />
        <line
          x1={Math.sqrt(UNINFORMATIVE_ETA) * barW}
          x2={Math.sqrt(UNINFORMATIVE_ETA) * barW}
          y1={-1}
          y2={11}
          stroke={palette.failed}
          strokeDasharray="2,2"
        />
        <text x={0} y={22} fill={palette.textFaint} fontSize={8}>0</text>
        <text
          x={Math.sqrt(UNINFORMATIVE_ETA) * barW}
          y={22}
          fill={palette.textFaint}
          fontSize={8}
          textAnchor="middle"
        >
          {UNINFORMATIVE_ETA}
        </text>
        <text x={barW} y={22} fill={palette.textFaint} fontSize={8} textAnchor="end">1</text>
      </svg>

      <div
        style={{
          display: "flex",
          gap: 12,
          marginTop: 6,
          fontSize: 10,
          color: palette.textFaint,
        }}
      >
        <span>between {between.toExponential(1)}</span>
        <span>within {within.toExponential(1)}</span>
        <span>{n_types} types</span>
        <span>{n_events} events</span>
      </div>

      {!informative && (
        <div
          style={{
            marginTop: 8,
            padding: "6px 8px",
            borderLeft: `2px solid ${palette.failed}`,
            background: palette.bgSunken,
            fontSize: 10,
            lineHeight: 1.5,
            color: palette.textDim,
          }}
        >
          Below the flagging threshold: the event types do not discriminate, so a
          law comparison on this corpus cannot adjudicate the typing. A non-trivial
          correlation may still appear — it is carried by cascade-length variation,
          not by type identity — and is <strong>not</strong> evidence that the
          typing is correct. A negative result here is evidence about the
          observable, not about the process.
        </div>
      )}
    </div>
  );
}

/**
 * Floor estimates by receiver.
 *
 * A positive floor is only evidence for a positive floor if the estimator that
 * produced it could have returned something else. The sample minimum is
 * bounded below by its own sample and so cannot; the asymptotic intercept can.
 *
 * The chart therefore encodes falsifiability as a first-class visual property
 * — a hatched bar for an unfalsifiable estimate, with the reason stated —
 * rather than reporting a number that reads as confirmation either way.
 */

import type { ReceiverFloor } from "../../connection/protocol";
import { mono, palette } from "../../theme";

interface Props {
  receivers: ReceiverFloor[];
  selected: string | null;
  onSelect: (receiver: string) => void;
  width?: number;
}

export function FloorPanel({ receivers, selected, onSelect, width = 360 }: Props) {
  if (receivers.length === 0) {
    return (
      <div style={{ padding: 24, color: palette.textFaint, fontSize: 11, fontFamily: mono }}>
        Run an analysis to estimate floors
      </div>
    );
  }

  const max = Math.max(...receivers.map((r) => Math.abs(r.floor)), 1e-9);
  const anyUnfalsifiable = receivers.some((r) => !r.falsifiable);
  const anyUnsupported = receivers.some((r) => !r.supports_positive_floor);
  const barW = width - 150;

  return (
    <div style={{ width, fontFamily: mono, fontSize: 11 }}>
      <svg width={0} height={0}>
        <defs>
          {/* Hatching marks an estimate that could not have come out otherwise. */}
          <pattern id="unfalsifiable" width="6" height="6" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
            <rect width="6" height="6" fill={palette.unfalsifiable} opacity={0.25} />
            <line x1="0" y1="0" x2="0" y2="6" stroke={palette.unfalsifiable} strokeWidth="2" />
          </pattern>
        </defs>
      </svg>

      {receivers.map((r) => {
        const dim = selected !== null && selected !== r.receiver;
        return (
          <div
            key={r.receiver}
            onClick={() => onSelect(r.receiver)}
            title={
              r.falsifiable
                ? `${r.estimator}: can return a non-positive value, so this estimate could have failed`
                : `${r.estimator}: bounded below by its own sample and cannot return a non-positive value`
            }
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "3px 4px",
              cursor: "pointer",
              opacity: dim ? 0.35 : 1,
              background: selected === r.receiver ? palette.bgElevated : "transparent",
              borderRadius: 2,
            }}
          >
            <span style={{ width: 64, color: palette.textDim }}>{r.receiver}</span>

            <svg width={barW} height={12}>
              <rect width={barW} height={12} fill={palette.bgSunken} rx={2} />
              <rect
                width={Math.max((Math.abs(r.floor) / max) * barW, 2)}
                height={12}
                rx={2}
                fill={r.falsifiable ? palette.falsifiable : "url(#unfalsifiable)"}
              />
              {/* A floor at or below zero is the falsifying observation. */}
              {r.floor <= 0 && <rect width={barW} height={12} rx={2} fill={palette.failed} opacity={0.4} />}
            </svg>

            <span style={{ width: 58, textAlign: "right", color: palette.text }}>
              {r.floor.toExponential(2)}
            </span>

            <span
              style={{
                width: 12,
                textAlign: "center",
                color: r.supports_positive_floor ? palette.resolved : palette.warn,
              }}
            >
              {r.supports_positive_floor ? "✓" : "!"}
            </span>
          </div>
        );
      })}

      {anyUnfalsifiable && (
        <Note colour={palette.unfalsifiable}>
          Hatched bars come from an estimator bounded below by its own sample. It
          returns a positive value on every input, including a process with no
          floor, so its positivity is not evidence for a positive floor.
        </Note>
      )}

      {anyUnsupported && (
        <Note colour={palette.warn}>
          A receiver marked <strong>!</strong> has an estimate within noise of
          zero, or from an estimator that cannot falsify. It does not support a
          positive floor regardless of its sign.
        </Note>
      )}
    </div>
  );
}

function Note({ colour, children }: { colour: string; children: React.ReactNode }) {
  return (
    <div
      style={{
        marginTop: 8,
        padding: "6px 8px",
        borderLeft: `2px solid ${colour}`,
        background: palette.bgSunken,
        fontSize: 10,
        lineHeight: 1.5,
        color: palette.textDim,
      }}
    >
      {children}
    </div>
  );
}

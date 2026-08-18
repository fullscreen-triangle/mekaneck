/**
 * Run outcomes.
 *
 * An inquiry terminates in one of two ways and neither is an error. The
 * interface must not collapse the second into the first: a contested closure
 * carries several incompatible cells, and picking one to display would assert
 * a discrimination the evidence does not license.
 *
 * A declination is therefore given equal visual weight to a resolution — its
 * own colour, distinct from failure — and every reached cell is shown with the
 * catalysts that reached it, so a reader can see where the disagreement lies.
 */

import type { BindingResult, TraceStep } from "../../connection/protocol";
import { mono, palette } from "../../theme";

interface Props {
  bindings: BindingResult[];
  width?: number;
}

export function OutcomePanel({ bindings, width = 360 }: Props) {
  if (bindings.length === 0) {
    return (
      <div style={{ padding: 24, color: palette.textFaint, fontSize: 11, fontFamily: mono }}>
        Run a program to see its outcome
      </div>
    );
  }

  return (
    <div style={{ width, fontFamily: mono, fontSize: 11 }}>
      {bindings.map((b) => (
        <Binding key={b.name} binding={b} width={width} />
      ))}
    </div>
  );
}

function Binding({ binding, width }: { binding: BindingResult; width: number }) {
  const resolved = binding.outcome.outcome === "resolved";
  const colour = resolved ? palette.resolved : palette.contested;

  return (
    <div
      style={{
        marginBottom: 10,
        border: `1px solid ${palette.border}`,
        borderLeft: `3px solid ${colour}`,
        borderRadius: 3,
        background: palette.bgSunken,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "6px 8px",
          borderBottom: `1px solid ${palette.borderSubtle}`,
        }}
      >
        <span style={{ color: palette.text, fontWeight: 600 }}>{binding.name}</span>
        <span style={{ color: colour, fontSize: 10, letterSpacing: "0.05em" }}>
          {resolved ? "CONVERGENT CLOSURE" : "CONTESTED CLOSURE"}
        </span>
      </div>

      <div style={{ padding: "8px" }}>
        {binding.outcome.outcome === "resolved" ? (
          <div style={{ color: palette.resolved, fontSize: 13 }}>
            {binding.outcome.cell}
          </div>
        ) : (
          <>
            <p
              style={{
                margin: "0 0 8px",
                fontSize: 10,
                lineHeight: 1.5,
                color: palette.textDim,
              }}
            >
              No single cell is supported. {binding.outcome.cells.length} incompatible
              cells were reached; the evidence does not license a choice among them.
              This is a normal termination, not a failure.
            </p>
            {binding.outcome.cells.map((cell) => (
              <CellRow
                key={cell}
                cell={cell}
                reachedBy={binding.trace.filter((t) => t.cell === cell)}
                width={width - 32}
              />
            ))}
          </>
        )}

        <div
          style={{
            marginTop: 8,
            paddingTop: 6,
            borderTop: `1px solid ${palette.borderSubtle}`,
            fontSize: 10,
            color: palette.textFaint,
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <span>record {binding.record}</span>
          <span>{binding.trace.length} invocation{binding.trace.length === 1 ? "" : "s"}</span>
        </div>
      </div>
    </div>
  );
}

function CellRow({
  cell,
  reachedBy,
  width,
}: {
  cell: string;
  reachedBy: TraceStep[];
  width: number;
}) {
  return (
    <div
      style={{
        width,
        display: "flex",
        alignItems: "baseline",
        gap: 8,
        padding: "3px 6px",
        marginBottom: 3,
        background: palette.bg,
        borderRadius: 2,
        borderLeft: `2px solid ${palette.contested}`,
      }}
    >
      <span style={{ color: palette.text, minWidth: 70 }}>{cell}</span>
      <span style={{ color: palette.textFaint, fontSize: 10 }}>
        via {reachedBy.map((t) => t.catalyst).join(", ") || "—"}
      </span>
    </div>
  );
}

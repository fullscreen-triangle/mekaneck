/**
 * Composition-law comparison.
 *
 * The design constraint that shapes this chart: rows computed under
 * instance-specific estimation are algebraic identities. They report a perfect
 * fit on data from any process whatsoever, so presenting them beside
 * type-averaged rows on equal footing would assert something the papers prove
 * is unwarranted.
 *
 * They are therefore shown in a separate, muted band, labelled, and carrying
 * the reason. They are not hidden — seeing r = 1.000 marked as an identity is
 * more instructive than not seeing it at all.
 */

import { useMemo } from "react";

import type { LawRow } from "../../connection/protocol";
import { mono, palette, regimeStyle } from "../../theme";

interface Props {
  laws: LawRow[];
  selectedLaw: string | null;
  onSelectLaw: (law: string) => void;
  showNonEvidential: boolean;
  onToggleNonEvidential: () => void;
  width?: number;
}

export function LawComparison({
  laws,
  selectedLaw,
  onSelectLaw,
  showNonEvidential,
  onToggleNonEvidential,
  width = 360,
}: Props) {
  const { evidential, identities } = useMemo(
    () => ({
      evidential: laws.filter((l) => l.evidential),
      identities: laws.filter((l) => !l.evidential),
    }),
    [laws],
  );

  if (laws.length === 0) {
    return <Empty width={width} label="Run an analysis to compare laws" />;
  }

  // Rank only among rows that can carry evidence.
  const best = evidential.reduce<LawRow | null>(
    (a, b) => (a === null || (b.pearson_r ?? -2) > (a.pearson_r ?? -2) ? b : a),
    null,
  );

  return (
    <div style={{ width, fontFamily: mono, fontSize: 11 }}>
      <Section title="Type-averaged — these can fail">
        {evidential.map((l) => (
          <LawBar
            key={`${l.law}-${l.estimation}`}
            row={l}
            width={width}
            isBest={best?.law === l.law}
            selected={selectedLaw === l.law}
            onClick={() => onSelectLaw(l.law)}
          />
        ))}
      </Section>

      <button
        onClick={onToggleNonEvidential}
        style={{
          width: "100%",
          marginTop: 10,
          padding: "5px 8px",
          background: "transparent",
          border: `1px solid ${palette.border}`,
          borderRadius: 3,
          color: palette.textDim,
          fontFamily: mono,
          fontSize: 10,
          cursor: "pointer",
          textAlign: "left",
        }}
      >
        {showNonEvidential ? "▾" : "▸"} Instance-specific ({identities.length}) —
        algebraic identities, not evidence
      </button>

      {showNonEvidential && (
        <div
          style={{
            marginTop: 6,
            padding: "8px",
            background: palette.bgSunken,
            borderLeft: `2px solid ${palette.identity}`,
            borderRadius: 2,
          }}
        >
          <p
            style={{
              margin: "0 0 8px",
              fontSize: 10,
              lineHeight: 1.5,
              color: palette.textFaint,
            }}
          >
            {regimeStyle(false).caveat}
          </p>
          {identities.map((l) => (
            <LawBar
              key={`${l.law}-${l.estimation}`}
              row={l}
              width={width - 24}
              isBest={false}
              selected={false}
              muted
            />
          ))}
        </div>
      )}
    </div>
  );
}

function LawBar({
  row,
  width,
  isBest,
  selected,
  muted = false,
  onClick,
}: {
  row: LawRow;
  width: number;
  isBest: boolean;
  selected: boolean;
  muted?: boolean;
  onClick?: () => void;
}) {
  const r = row.pearson_r;
  const style = regimeStyle(row.evidential);
  const barW = width - 150;
  // r ranges over [-1, 1]; map to a bar with zero at the centre.
  const frac = r === null ? 0 : (r + 1) / 2;

  return (
    <div
      onClick={onClick}
      title={
        r === null
          ? "Correlation undefined: the predictor is constant on this corpus"
          : undefined
      }
      style={{
        display: "flex",
        alignItems: "center",
        gap: 6,
        padding: "3px 4px",
        cursor: onClick ? "pointer" : "default",
        background: selected ? palette.bgElevated : "transparent",
        borderRadius: 2,
        opacity: muted ? 0.75 : 1,
      }}
    >
      <span
        style={{
          width: 74,
          color: isBest ? palette.textBright : palette.textDim,
          fontWeight: isBest ? 600 : 400,
        }}
      >
        {row.law.replace("_", " ").slice(0, 9)}
      </span>

      <div
        style={{
          width: barW,
          height: 10,
          background: palette.bgSunken,
          borderRadius: 2,
          position: "relative",
        }}
      >
        {/* zero mark, because a negative correlation must be visible as such */}
        <div
          style={{
            position: "absolute",
            left: barW / 2,
            top: -1,
            width: 1,
            height: 12,
            background: palette.textFaint,
          }}
        />
        {r !== null && (
          <div
            style={{
              position: "absolute",
              left: r >= 0 ? barW / 2 : barW * frac,
              width: Math.abs(barW * frac - barW / 2),
              height: 10,
              background: style.colour,
              borderRadius: 1,
            }}
          />
        )}
      </div>

      <span style={{ width: 46, textAlign: "right", color: style.colour }}>
        {r === null ? "n/a" : r.toFixed(3)}
      </span>
      <span style={{ width: 44, textAlign: "right", color: palette.textFaint }}>
        {row.rmse === null ? "—" : row.rmse.toFixed(3)}
      </span>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <div
        style={{
          fontSize: 10,
          color: palette.textDim,
          textTransform: "uppercase",
          letterSpacing: "0.06em",
          marginBottom: 4,
        }}
      >
        {title}
      </div>
      {children}
    </div>
  );
}

function Empty({ width, label }: { width: number; label: string }) {
  return (
    <div
      style={{
        width,
        padding: 24,
        textAlign: "center",
        color: palette.textFaint,
        fontSize: 11,
        fontFamily: mono,
      }}
    >
      {label}
    </div>
  );
}

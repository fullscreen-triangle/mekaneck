/**
 * Source editor with live diagnostics.
 *
 * Diagnostics come from the local TypeScript checker, which is pinned to the
 * binary by the shared fixture suite — so the editor cannot disagree with the
 * compiler about whether a program is well formed. The binary re-checks on
 * run; this is the fast path, not the authority.
 *
 * The two structural keywords (`seek`/`excluding`) are highlighted distinctly
 * from ordinary keywords, because the exclusion clause is the one syntactic
 * commitment the language will not let a program omit.
 */

import { useMemo } from "react";

import { diagnose, type FloorValues } from "../../languages/mekaneck/checker";
import { mono, palette } from "../../theme";

const KEYWORDS = new Set([
  "substrate", "receivers", "observable", "events", "floor", "catalyst",
  "independent", "let", "report", "resolved", "decline", "record",
]);
const STRUCTURAL = new Set(["seek", "excluding", "via", "until", "closure"]);

type Tok = { type: keyof typeof COLOURS; text: string };

const COLOURS = {
  keyword: palette.synKeyword,
  structural: palette.synStructural,
  builtin: palette.synBuiltin,
  string: palette.synString,
  comment: palette.synComment,
  number: palette.synNumber,
  ident: palette.synIdent,
  punct: palette.synPunct,
  ws: palette.synPunct,
} as const;

function tokenize(line: string): Tok[] {
  const out: Tok[] = [];
  let i = 0;
  while (i < line.length) {
    const c = line[i];
    if (c === "#") {
      out.push({ type: "comment", text: line.slice(i) });
      break;
    }
    if (c === '"') {
      let j = i + 1;
      while (j < line.length && line[j] !== '"') j += 1;
      out.push({ type: "string", text: line.slice(i, j + 1) });
      i = j + 1;
      continue;
    }
    if (/\s/.test(c)) {
      let j = i;
      while (j < line.length && /\s/.test(line[j])) j += 1;
      out.push({ type: "ws", text: line.slice(i, j) });
      i = j;
      continue;
    }
    if (/[A-Za-z_]/.test(c)) {
      let j = i;
      while (j < line.length && /[A-Za-z0-9_]/.test(line[j])) j += 1;
      const w = line.slice(i, j);
      // An identifier immediately followed by "(" is a substrate builtin.
      const isCall = line[j] === "(";
      out.push({
        type: STRUCTURAL.has(w)
          ? "structural"
          : KEYWORDS.has(w)
            ? "keyword"
            : isCall
              ? "builtin"
              : "ident",
        text: w,
      });
      i = j;
      continue;
    }
    if (/[0-9]/.test(c)) {
      let j = i;
      while (j < line.length && /[0-9.]/.test(line[j])) j += 1;
      out.push({ type: "number", text: line.slice(i, j) });
      i = j;
      continue;
    }
    out.push({ type: "punct", text: c });
    i += 1;
  }
  return out;
}

interface Props {
  content: string;
  floors: FloorValues;
  fileName: string;
}

export function Editor({ content, floors, fileName }: Props) {
  const diagnostics = useMemo(() => diagnose(content, floors), [content, floors]);
  const byLine = useMemo(() => {
    const m = new Map<number, typeof diagnostics>();
    for (const d of diagnostics) {
      const list = m.get(d.line) ?? [];
      list.push(d);
      m.set(d.line, list);
    }
    return m;
  }, [diagnostics]);

  const lines = content.split("\n");

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0, background: palette.bg }}>
      <div
        style={{
          height: 34,
          background: palette.bgElevated,
          display: "flex",
          alignItems: "stretch",
          flexShrink: 0,
        }}
      >
        <div
          style={{
            background: palette.bg,
            padding: "0 14px",
            display: "flex",
            alignItems: "center",
            gap: 8,
            fontSize: 12,
            color: palette.textBright,
            borderTop: `1px solid ${palette.accent}`,
          }}
        >
          {fileName}
          {diagnostics.length > 0 && (
            <span
              style={{
                fontSize: 10,
                color: diagnostics.some((d) => d.severity === "error")
                  ? palette.failed
                  : palette.warn,
              }}
            >
              {diagnostics.length}
            </span>
          )}
        </div>
      </div>

      <div
        style={{
          flex: 1,
          overflow: "auto",
          fontFamily: mono,
          fontSize: 13,
          lineHeight: "20px",
          padding: "8px 0",
        }}
      >
        {lines.map((line, idx) => {
          const lineNo = idx + 1;
          const diags = byLine.get(lineNo);
          const worst = diags?.some((d) => d.severity === "error")
            ? palette.failed
            : diags
              ? palette.warn
              : null;

          return (
            <div key={idx}>
              <div style={{ display: "flex", minHeight: 20, background: worst ? `${worst}12` : undefined }}>
                <span
                  style={{
                    width: 46,
                    textAlign: "right",
                    paddingRight: 14,
                    color: worst ?? "#5a5a5a",
                    fontSize: 12,
                    userSelect: "none",
                    flexShrink: 0,
                  }}
                >
                  {lineNo}
                </span>
                <span style={{ whiteSpace: "pre" }}>
                  {tokenize(line).map((t, j) => (
                    <span key={j} style={{ color: COLOURS[t.type] }}>
                      {t.text}
                    </span>
                  ))}
                </span>
              </div>

              {diags?.map((d, j) => (
                <div
                  key={j}
                  style={{
                    display: "flex",
                    fontSize: 11,
                    color: d.severity === "error" ? palette.failed : palette.warn,
                    background: `${d.severity === "error" ? palette.failed : palette.warn}0e`,
                    padding: "2px 0 4px 60px",
                    lineHeight: 1.45,
                  }}
                >
                  <span style={{ marginRight: 6 }}>{d.severity === "error" ? "✕" : "▲"}</span>
                  <span>{d.message}</span>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/**
 * The IDE shell.
 *
 * Layout follows an editor convention so the tool is immediately legible:
 * activity bar, explorer, editor, results panel, status bar. What differs from
 * a conventional IDE is what the status bar reports and what the panels
 * refuse to say.
 *
 * The connection banner states where data is going, because "local only" is a
 * property a user should be able to verify rather than take on trust.
 */

import { useMemo, useState } from "react";

import { LawComparison } from "../charts/LawComparison";
import { FloorPanel } from "../charts/FloorPanel";
import { SeparationGauge } from "../charts/SeparationGauge";
import { CardiacPanel } from "../panels/CardiacPanel";
import { OutcomePanel } from "../panels/OutcomePanel";
import { Editor } from "./Editor";
import { useStore, toggle } from "../../state/store";
import { mono, palette, sans } from "../../theme";

const PANELS = ["Console", "Outcome", "Floors", "Laws", "Separation", "Cardiac"] as const;

export function App() {
  const {
    files, openPath, setOpenPath, activeFile,
    analysis, bindings, log,
    selection, select, clearSelection,
    activePanel, setActivePanel,
    connection,
  } = useStore();

  const file = activeFile();

  // Floors known from the last analysis feed the editor's local checker, so
  // T-Seek-Pos is checked against real values rather than assumed.
  const floors = useMemo(() => {
    const m: Record<string, number> = {};
    for (const r of analysis?.receivers ?? []) m[r.receiver] = r.floor;
    return m;
  }, [analysis]);

  const filterActive =
    selection.receiver !== null || selection.eventType !== null || selection.law !== null;

  return (
    <div
      style={{
        width: "100%",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        background: palette.bg,
        color: palette.text,
        fontFamily: sans,
        overflow: "hidden",
      }}
    >
      <ConnectionBanner state={connection} />

      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        <ActivityBar />

        <div
          style={{
            width: 230,
            background: palette.bgPanel,
            borderRight: `1px solid ${palette.borderSubtle}`,
            display: "flex",
            flexDirection: "column",
            flexShrink: 0,
          }}
        >
          <SectionLabel>Explorer</SectionLabel>
          {files.map((f) => (
            <div
              key={f.path}
              onClick={() => setOpenPath(f.path)}
              style={{
                padding: "4px 12px 4px 22px",
                fontSize: 12,
                cursor: "pointer",
                color: openPath === f.path ? palette.textBright : palette.text,
                background: openPath === f.path ? "#37373d" : "transparent",
              }}
            >
              {f.name}
            </div>
          ))}
        </div>

        {file ? (
          <Editor content={file.content} floors={floors} fileName={file.name} />
        ) : (
          <div
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: palette.textFaint,
              fontSize: 13,
            }}
          >
            Open a .mck file to begin
          </div>
        )}

        <div
          style={{
            width: 396,
            background: palette.bg,
            borderLeft: `1px solid ${palette.border}`,
            display: "flex",
            flexDirection: "column",
            flexShrink: 0,
          }}
        >
          <div
            style={{
              height: 34,
              background: palette.bgPanel,
              display: "flex",
              alignItems: "stretch",
              flexShrink: 0,
            }}
          >
            {PANELS.map((p) => (
              <div
                key={p}
                onClick={() => setActivePanel(p)}
                style={{
                  padding: "0 11px",
                  display: "flex",
                  alignItems: "center",
                  fontSize: 11,
                  cursor: "pointer",
                  color: activePanel === p ? palette.textBright : palette.textDim,
                  background: activePanel === p ? palette.bg : "transparent",
                  borderBottom: `1px solid ${activePanel === p ? palette.accent : "transparent"}`,
                }}
              >
                {p}
              </div>
            ))}
          </div>

          {filterActive && (
            <div
              style={{
                padding: "4px 10px",
                fontSize: 10,
                fontFamily: mono,
                color: palette.textDim,
                background: palette.bgSunken,
                display: "flex",
                gap: 8,
                alignItems: "center",
              }}
            >
              <span>filtered:</span>
              {selection.receiver && <Chip>{selection.receiver}</Chip>}
              {selection.eventType && <Chip>{selection.eventType}</Chip>}
              {selection.law && <Chip>{selection.law}</Chip>}
              <span
                onClick={clearSelection}
                style={{ marginLeft: "auto", cursor: "pointer", color: palette.accent }}
              >
                clear
              </span>
            </div>
          )}

          <div style={{ flex: 1, overflow: "auto", padding: 10 }}>
            {activePanel === "Console" && <Console log={log} />}
            {activePanel === "Outcome" && <OutcomePanel bindings={bindings} width={376} />}
            {activePanel === "Floors" && (
              <FloorPanel
                receivers={analysis?.receivers ?? []}
                selected={selection.receiver}
                onSelect={(r) => select(toggle(selection, "receiver", r))}
                width={376}
              />
            )}
            {activePanel === "Laws" && (
              <LawComparison
                laws={analysis?.laws ?? []}
                selectedLaw={selection.law}
                onSelectLaw={(l) => select(toggle(selection, "law", l))}
                showNonEvidential={selection.showNonEvidential}
                onToggleNonEvidential={() =>
                  select({ showNonEvidential: !selection.showNonEvidential })
                }
                width={376}
              />
            )}
            {activePanel === "Cardiac" && <CardiacPanel width={376} />}
            {activePanel === "Separation" && (
              <SeparationGauge separation={analysis?.separation ?? null} width={376} />
            )}
          </div>
        </div>
      </div>

      <StatusBar />
    </div>
  );
}

function ConnectionBanner({ state }: { state: ReturnType<typeof useStore.getState>["connection"] }) {
  const [text, colour] =
    state.status === "ready"
      ? [`Paired with a binary on ${state.boundTo} — nothing leaves this machine`, palette.resolved]
      : state.status === "denied"
        ? [`Pairing refused: ${state.reason}`, palette.failed]
        : state.status === "closed"
          ? [state.reason, palette.warn]
          : state.status === "connecting"
            ? ["Connecting…", palette.textDim]
            : ["Not paired — run `mekaneck serve` and enter its token", palette.textDim];

  return (
    <div
      style={{
        height: 26,
        display: "flex",
        alignItems: "center",
        padding: "0 12px",
        fontSize: 11,
        color: colour,
        background: palette.bgActivity,
        borderBottom: `1px solid ${palette.borderSubtle}`,
        flexShrink: 0,
      }}
    >
      <span style={{ marginRight: 8 }}>●</span>
      {text}
    </div>
  );
}

function ActivityBar() {
  const { activityView, setActivityView } = useStore();
  const items = [
    ["files", "Explorer"],
    ["run", "Run"],
    ["analyse", "Analyse"],
  ] as const;
  return (
    <div
      style={{
        width: 44,
        background: palette.bgActivity,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        paddingTop: 6,
        flexShrink: 0,
      }}
    >
      {items.map(([id, label]) => (
        <div
          key={id}
          title={label}
          onClick={() => setActivityView(id)}
          style={{
            width: 44,
            height: 44,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            fontSize: 10,
            color: activityView === id ? palette.textBright : "#858585",
            borderLeft: `2px solid ${activityView === id ? palette.textBright : "transparent"}`,
          }}
        >
          {label.slice(0, 3)}
        </div>
      ))}
    </div>
  );
}

function Console({ log }: { log: ReturnType<typeof useStore.getState>["log"] }) {
  const colour = {
    info: palette.textDim,
    exec: palette.evidential,
    warn: palette.warn,
    ok: palette.resolved,
    contested: palette.contested,
    error: palette.failed,
  } as const;

  if (log.length === 0) {
    return <div style={{ color: palette.textFaint, fontSize: 11, fontFamily: mono }}>No output</div>;
  }

  return (
    <div style={{ fontFamily: mono, fontSize: 11, lineHeight: 1.6 }}>
      {log.map((l, i) => (
        <div key={i} style={{ color: colour[l.kind], display: "flex", gap: 8 }}>
          <span style={{ color: palette.textFaint, flexShrink: 0 }}>
            {l.record !== undefined ? String(l.record).padStart(4) : "    "}
          </span>
          <span>{l.text}</span>
        </div>
      ))}
    </div>
  );
}

function StatusBar() {
  const { analysis, bindings, connection } = useStore();
  const declined = bindings.filter((b) => b.outcome.outcome === "declined").length;
  const record = bindings.reduce((s, b) => s + b.record, 0);

  return (
    <div
      style={{
        height: 22,
        background: connection.status === "ready" ? palette.accent : "#4a4a4a",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 10px",
        fontSize: 11,
        color: "#fff",
        flexShrink: 0,
      }}
    >
      <div style={{ display: "flex", gap: 14 }}>
        <span>{connection.status === "ready" ? "local binary" : "not paired"}</span>
        {record > 0 && <span>record {record}</span>}
        {analysis && <span>{analysis.cascades} cascades</span>}
        {analysis && (
          <span>
            η {analysis.separation.eta < 1e-3
              ? analysis.separation.eta.toExponential(1)
              : analysis.separation.eta.toFixed(3)}
            {!analysis.separation.informative && " (uninformative)"}
          </span>
        )}
        {declined > 0 && <span>{declined} contested</span>}
      </div>
      <span>Mekaneck</span>
    </div>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        padding: "8px 12px",
        fontSize: 11,
        color: "#bbb",
        textTransform: "uppercase",
        letterSpacing: "0.08em",
        fontWeight: 600,
      }}
    >
      {children}
    </div>
  );
}

function Chip({ children }: { children: React.ReactNode }) {
  return (
    <span
      style={{
        background: palette.bgElevated,
        padding: "1px 6px",
        borderRadius: 2,
        color: palette.text,
      }}
    >
      {children}
    </span>
  );
}

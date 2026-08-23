/**
 * IDE state.
 *
 * Results arrive from the local binary through `MekaneckClient` and are stored
 * exactly as received — the store performs no interpretation. In particular it
 * does not collapse a declination to a single cell, and it does not discard
 * the `evidential` flag on a law row. Panels render what the kernel said.
 */

import { create } from "zustand";

import type {
  BindingResult,
  Diagnostic,
  LawRow,
  ReceiverFloor,
  SeparationReport,
} from "../connection/protocol";
import { MekaneckClient, type ConnectionState } from "../connection/socket";

export interface SourceFile {
  name: string;
  path: string;
  content: string;
}

/** A cross-panel filter. Selecting in one chart filters the others. */
export interface Selection {
  receiver: string | null;
  eventType: string | null;
  law: string | null;
  /** When false, rows computed under instance-specific estimation are hidden. */
  showNonEvidential: boolean;
}

export interface AnalysisState {
  substrate: string;
  receivers: ReceiverFloor[];
  cascades: number;
  separation: SeparationReport;
  laws: LawRow[];
}

export interface LogLine {
  kind: "info" | "exec" | "warn" | "ok" | "contested" | "error";
  text: string;
  /** Monotone committed record at the time of the line, when known. */
  record?: number;
}

interface Store {
  // ---- connection ----
  client: MekaneckClient | null;
  connection: ConnectionState;
  connect: (token: string, url?: string) => Promise<void>;
  disconnect: () => void;

  // ---- workspace ----
  files: SourceFile[];
  openPath: string | null;
  setOpenPath: (p: string) => void;
  updateContent: (path: string, content: string) => void;
  activeFile: () => SourceFile | null;

  // ---- results ----
  diagnostics: Diagnostic[];
  bindings: BindingResult[];
  analysis: AnalysisState | null;
  log: LogLine[];
  appendLog: (l: LogLine) => void;

  setDiagnostics: (d: Diagnostic[]) => void;
  setBindings: (b: BindingResult[]) => void;
  setAnalysis: (a: AnalysisState | null) => void;

  // ---- view ----
  selection: Selection;
  select: (patch: Partial<Selection>) => void;
  clearSelection: () => void;
  activePanel: string;
  setActivePanel: (p: string) => void;
  activityView: string;
  setActivityView: (v: string) => void;
}

const EMPTY_SELECTION: Selection = {
  receiver: null,
  eventType: null,
  law: null,
  showNonEvidential: true,
};

export const useStore = create<Store>((set, get) => ({
  client: null,
  connection: { status: "idle" },

  async connect(token, url) {
    const client = new MekaneckClient({
      token,
      url,
      onState: (connection) => set({ connection }),
    });
    set({ client });
    await client.connect();
    const s = get().connection;
    if (s.status === "ready") {
      get().appendLog({
        kind: "ok",
        text: `paired with ${s.serverVersion} on ${s.boundTo}`,
      });
    }
  },

  disconnect() {
    get().client?.close();
    set({ client: null, connection: { status: "idle" } });
  },

  files: [],
  openPath: null,
  setOpenPath: (openPath) => set({ openPath }),
  updateContent: (path, content) =>
    set((s) => ({
      files: s.files.map((f) => (f.path === path ? { ...f, content } : f)),
    })),
  activeFile: () => {
    const { files, openPath } = get();
    return files.find((f) => f.path === openPath) ?? null;
  },

  diagnostics: [],
  bindings: [],
  analysis: null,
  log: [],
  appendLog: (l) => set((s) => ({ log: [...s.log, l] })),

  setDiagnostics: (diagnostics) => set({ diagnostics }),
  setBindings: (bindings) => set({ bindings }),
  setAnalysis: (analysis) => set({ analysis }),

  selection: EMPTY_SELECTION,
  select: (patch) => set((s) => ({ selection: { ...s.selection, ...patch } })),
  clearSelection: () => set({ selection: EMPTY_SELECTION }),

  // An unpaired session opens on Pair: the Console has nothing in it until a
  // binary is connected, and landing there reads as a tool that is broken
  // rather than one that is waiting for a token.
  activePanel: "Pair",
  setActivePanel: (activePanel) => set({ activePanel }),
  activityView: "files",
  setActivityView: (activityView) => set({ activityView }),
}));

/** Toggle a selection facet: clicking the active value clears it. */
export function toggle<K extends keyof Selection>(
  current: Selection,
  key: K,
  value: Selection[K],
): Partial<Selection> {
  return { [key]: current[key] === value ? null : value } as Partial<Selection>;
}

/**
 * Summarise a run for the log.
 *
 * A declination gets its own kind rather than `error`: contested closure is a
 * normal termination and reporting it as a failure is the mistake the closure
 * criterion exists to prevent.
 */
export function summariseBinding(b: BindingResult): LogLine {
  if (b.outcome.outcome === "resolved") {
    return {
      kind: "ok",
      text: `${b.name}: resolved ${b.outcome.cell}`,
      record: b.record,
    };
  }
  return {
    kind: "contested",
    text:
      `${b.name}: declined — ${b.outcome.cells.length} incompatible cells ` +
      `(${b.outcome.cells.join(", ")}). No single cell is supported by the ` +
      `evidence; this is a normal termination, not a failure.`,
    record: b.record,
  };
}

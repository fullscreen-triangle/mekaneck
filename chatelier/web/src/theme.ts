/**
 * Visual language for the IDE.
 *
 * Colour carries meaning here rather than decoration, and three of the
 * assignments are load-bearing — they encode distinctions the papers say a
 * client must not lose:
 *
 * - `evidential` vs `identity`: a result computed under instance-specific
 *   estimation is an algebraic identity, not a finding. It is rendered in a
 *   muted, explicitly marked style so it can never be mistaken for the
 *   type-averaged row above it.
 * - `resolved` vs `contested`: a declination is a normal termination, so it
 *   is not styled as an error. It gets its own colour, distinct from both
 *   success and failure.
 * - `falsifiable` vs `unfalsifiable`: a floor from an estimator that cannot
 *   return a non-positive value is not evidence for a positive floor.
 */

export const palette = {
  // surfaces, VS Code-adjacent so the shell reads as an editor
  bg: "#1e1e1e",
  bgPanel: "#252526",
  bgActivity: "#333333",
  bgElevated: "#2d2d2d",
  bgSunken: "#151b26",
  border: "#2a3545",
  borderSubtle: "#1e2a3a",

  text: "#d4d4d4",
  textDim: "#8a95a5",
  textFaint: "#5a6a7d",
  textBright: "#ffffff",

  accent: "#007acc",

  // ---- semantics that must not be conflated ----

  /** A result that could have come out otherwise. */
  evidential: "#4a9fd8",
  /** An algebraic identity: perfect agreement that is not evidence. */
  identity: "#7a6a55",

  /** Convergent closure. */
  resolved: "#4caf6e",
  /** Contested closure — a normal termination, deliberately not red. */
  contested: "#c9a227",
  /** An actual failure: a request that could not be served. */
  failed: "#c45050",

  /** A floor estimate capable of contradicting the positivity claim. */
  falsifiable: "#4caf6e",
  /** A floor estimate that cannot come out non-positive. */
  unfalsifiable: "#e8a838",

  warn: "#e8a838",

  // syntax
  synKeyword: "#569cd6",
  synStructural: "#c586c0",
  synBuiltin: "#dcdcaa",
  synString: "#ce9178",
  synComment: "#6a9955",
  synNumber: "#b5cea8",
  synIdent: "#9cdcfe",
  synPunct: "#d4d4d4",
} as const;

export const mono =
  "'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace";
export const sans =
  "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";

/**
 * Threshold below which a type separation is reported as uninformative.
 * Mirrors `UNINFORMATIVE_ETA` in the algebra crate.
 */
export const UNINFORMATIVE_ETA = 0.05;

/** Colour for a separation value, by band. */
export function etaColour(eta: number): string {
  if (eta < UNINFORMATIVE_ETA) return palette.failed;
  if (eta < 0.3) return palette.warn;
  return palette.resolved;
}

/**
 * How a law row should be presented, given the regime it was computed under.
 *
 * The `caveat` is not optional decoration: a row that is not evidential must
 * carry an explanation wherever it appears, or the interface is asserting
 * something the papers prove is unwarranted.
 */
export function regimeStyle(evidential: boolean): {
  colour: string;
  label: string;
  caveat: string | null;
} {
  return evidential
    ? {
        colour: palette.evidential,
        label: "type-averaged",
        caveat: null,
      }
    : {
        colour: palette.identity,
        label: "instance-specific",
        caveat:
          "Algebraic identity: under instance-specific estimation the prediction " +
          "and the measurement are the same expression, so this agreement holds " +
          "for data from any process and is not evidence.",
      };
}

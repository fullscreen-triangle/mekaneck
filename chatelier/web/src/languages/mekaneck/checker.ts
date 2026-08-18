/**
 * Type checker for `.mck`.
 *
 * A mirror of `crates/lang/src/types.rs`. Two non-standard rules:
 *
 * - **T-Seek-Pos**: a substrate's floor must be strictly positive. A program
 *   may not assert an attainable zero residual.
 * - **T-Seek-Coh**: a `via` clause must name at least three *mutually*
 *   declared-independent catalysts, because no shorter support structure
 *   survives the loss of a member.
 *
 * What this cannot do — and neither can the Rust — is verify the independence
 * it requires. It requires the claim to be written down and auditable.
 */

import { MckError, lineCol, type Span } from "./lexer";
import { catalysts, lets, parse, reports, substrates, type Program } from "./parser";

/** Minimum catalysts for a robust support structure. */
export const MIN_COHERENCE = 3;

export type Severity = "error" | "warning";

export interface Diagnostic {
  message: string;
  span: Span;
  severity: Severity;
  line: number;
  column: number;
}

/** Substrate floors, supplied by bindings. The checker cannot compute them. */
export type FloorValues = Record<string, number>;

/**
 * Check a source buffer and return diagnostics.
 *
 * Mirrors `lang::diagnose`: a parse or type failure yields exactly one
 * diagnostic, and a substrate whose floor was not supplied yields a warning
 * rather than an error, because T-Seek-Pos simply went unchecked.
 */
export function diagnose(src: string, floors: FloorValues = {}): Diagnostic[] {
  let prog: Program;
  try {
    prog = parse(src);
  } catch (e) {
    return [toDiagnostic(src, e, "error")];
  }

  try {
    const unchecked = typecheck(prog, floors);
    return unchecked.map((s) => {
      const decl = substrates(prog).find((d) => d.name === s)!;
      return withPosition(src, {
        message:
          `floor for substrate "${s}" was not supplied, so T-Seek-Pos is unchecked; ` +
          "the declared estimator decides whether a positive result could have failed",
        span: decl.floor.span,
        severity: "warning",
      });
    });
  } catch (e) {
    return [toDiagnostic(src, e, "error")];
  }
}

/**
 * Type-check, returning the substrates whose floor was not supplied.
 * Throws `MckError` on the first failure, matching the Rust's `Result`.
 */
export function typecheck(prog: Program, floors: FloorValues): string[] {
  const bindings = new Map<string, string>();
  const independence = new Map<string, Set<string>>();

  for (const s of substrates(prog)) {
    if (bindings.has(s.name)) {
      throw new MckError(`"${s.name}" is declared more than once`, s.span);
    }
    bindings.set(s.name, "Substrate");
  }
  if (bindings.size === 0) {
    // No span: the absence of a declaration has no position.
    throw new MckError(
      "no substrate declared: a seek has no floor obligation to satisfy",
      { start: 0, end: 0 },
    );
  }

  for (const c of catalysts(prog)) {
    if (bindings.has(c.name)) {
      throw new MckError(`"${c.name}" is declared more than once`, c.span);
    }
    bindings.set(c.name, "Catalyst");
    independence.set(c.name, new Set(c.independent));
  }

  // An independence declaration naming an unknown catalyst is unverifiable in
  // a way the checker *can* detect.
  for (const c of catalysts(prog)) {
    for (const other of c.independent) {
      if (!independence.has(other)) {
        throw new MckError(`unknown catalyst "${other}"`, c.span);
      }
      if (other === c.name) {
        throw new MckError(
          `catalyst "${c.name}" is declared independent of itself`,
          c.span,
        );
      }
    }
  }

  // T-Seek-Pos, once per substrate: the floor is a property of the binding.
  const unchecked: string[] = [];
  for (const s of substrates(prog)) {
    const beta = floors[s.name];
    if (beta === undefined) {
      unchecked.push(s.name);
      continue;
    }
    if (Number.isNaN(beta) || beta <= 0) {
      throw new MckError(
        `substrate "${s.name}" declares floor ${fmt(beta)}, which is not strictly ` +
          "positive: a program may not assert an attainable zero residual",
        s.floor.span,
      );
    }
  }

  for (const l of lets(prog)) {
    checkSeek(l.seek, independence);
    bindings.set(l.name, "Outcome");
  }

  for (const r of reports(prog)) {
    if (!bindings.has(r.name)) {
      throw new MckError(`"${r.name}" is not bound`, r.span);
    }
  }

  return unchecked;
}

function checkSeek(
  seek: { via: string[]; viaSpan: Span | null; span: Span },
  independence: Map<string, Set<string>>,
): void {
  if (seek.via.length === 0) return; // no explicit chain: T-Seek-Coh does not apply
  const span = seek.viaSpan ?? seek.span;

  for (const c of seek.via) {
    if (!independence.has(c)) {
      throw new MckError(`unknown catalyst "${c}"`, span);
    }
  }

  const seen = new Set<string>();
  for (const c of seek.via) {
    if (seen.has(c)) {
      throw new MckError(
        `catalyst "${c}" appears more than once in the via clause`,
        span,
      );
    }
    seen.add(c);
  }

  if (seek.via.length < MIN_COHERENCE) {
    throw new MckError(
      `via names ${seek.via.length} catalyst(s); a support structure robust to the ` +
        `loss of any one member needs at least ${MIN_COHERENCE} (a 1-cycle is ` +
        "vacuous, a 2-cycle collapses)",
      span,
    );
  }

  // Checking the relation, not merely the count, is what distinguishes this
  // from a size heuristic.
  for (const a of seek.via) {
    for (const b of seek.via) {
      if (a === b) continue;
      if (!independence.get(a)!.has(b)) {
        throw new MckError(
          `catalysts "${a}" and "${b}" are not mutually declared independent`,
          span,
        );
      }
    }
  }
}

/** Render a float the way Rust's `{}` does, so messages match exactly. */
function fmt(n: number): string {
  return Number.isInteger(n) ? String(n) : String(n);
}

function withPosition(
  src: string,
  d: { message: string; span: Span; severity: Severity },
): Diagnostic {
  const { line, column } = lineCol(src, d.span);
  return { ...d, line, column };
}

function toDiagnostic(src: string, e: unknown, severity: Severity): Diagnostic {
  const span = e instanceof MckError ? e.span : { start: 0, end: 0 };
  const message = e instanceof Error ? e.message : String(e);
  return withPosition(src, { message, span, severity });
}

/**
 * Selection under a bounded budget, and relay provenance.
 *
 * A mirror of `crates/policy`, for the browser. As with the language
 * services, this is the fast local path and not the authority: the binary
 * re-selects when it runs.
 *
 * Two properties are carried deliberately and must not be simplified away:
 *
 * - the shadow price is the density of the first *excluded* candidate, not
 *   the last admitted one. The latter is not monotone in the budget and
 *   would rise as attention widens, which reads as the opposite of what is
 *   happening.
 * - a declined candidate is not a failed one. Under a bounded budget some
 *   declining is forced, and the UI must be able to say which.
 */

export interface Candidate {
  id: string;
  /** Cost of committing. Strictly positive. */
  cost: number;
  /** Value of committing, in the submitting module's units. May be negative. */
  gain: number;
}

export interface Budget {
  total: number;
  /** Lower bound on any candidate's cost. */
  floor: number;
}

export interface Selection {
  committed: string[];
  /** Declined for want of budget — not failures. */
  declined: string[];
  spent: number;
  totalGain: number;
  /** Density of the highest-density candidate excluded; null if all fit. */
  shadowPrice: number | null;
}

export function density(c: Candidate): number {
  return c.gain / c.cost;
}

/**
 * Most candidates committable per interval, whatever their gains.
 *
 * Declining beyond this is forced by boundedness, not by a judgement about
 * what was declined.
 */
export function maxCommitments(b: Budget): number {
  return Math.floor(b.total / b.floor);
}

/**
 * Select by threshold on gain density.
 *
 * Optimal for the continuous relaxation and within one candidate of the
 * integer optimum; exactly optimal when the repertoire is divisible.
 * Ties break by id so two runs of one protocol select the same set.
 */
export function select(candidates: readonly Candidate[], budget: Budget): Selection {
  const order = [...candidates].sort(
    (a, b) => density(b) - density(a) || a.id.localeCompare(b.id),
  );

  const committed: string[] = [];
  const declined: string[] = [];
  let spent = 0;
  let totalGain = 0;
  let shadowPrice: number | null = null;

  for (const c of order) {
    const affordable = spent + c.cost <= budget.total + 1e-12;
    if (affordable && density(c) > 0) {
      committed.push(c.id);
      spent += c.cost;
      totalGain += c.gain;
    } else {
      // The first candidate the budget excludes sets the price.
      if (shadowPrice === null && !affordable) shadowPrice = density(c);
      declined.push(c.id);
    }
  }

  return { committed, declined, spent, totalGain, shadowPrice };
}

/**
 * Whether every candidate is an independently selectable unit of equal cost.
 *
 * Stronger than "costs are multiples of the floor": bundling floor-sized
 * units into an indivisible candidate restores a 0/1 knapsack, where the
 * threshold rule is only within one candidate of the optimum.
 */
export function isDivisible(candidates: readonly Candidate[]): boolean {
  if (candidates.length === 0) return true;
  const first = candidates[0].cost;
  return candidates.every((c) => Math.abs(c.cost - first) < 1e-12);
}

// ---------------------------------------------------------------------------
// Relay provenance
// ---------------------------------------------------------------------------

export interface Relayed<T> {
  value: T;
  depth: number;
  /** Product of residual factors: the surviving fraction of the account. */
  fidelity: number;
}

export function origin<T>(value: T): Relayed<T> {
  return { value, depth: 0, fidelity: 1 };
}

/** Pass through one relay applying the given power. */
export function relay<T>(r: Relayed<T>, power: number): Relayed<T> {
  return { value: r.value, depth: r.depth + 1, fidelity: r.fidelity * (1 - power) };
}

/**
 * Accumulated drift: `1 - fidelity`.
 *
 * This is the composition of the relay powers. It is not a claim that the
 * account is false — no account resolves to a point, so there is no value to
 * compare against — only that content has drifted, without any relay having
 * altered it on purpose.
 */
export function drift<T>(r: Relayed<T>): number {
  return 1 - r.fidelity;
}

/** Worst-case fidelity after `depth` relays given a lower bound on powers. */
export function fidelityBound(depth: number, minPower: number): number {
  return Math.pow(1 - minPower, depth);
}

/** Relays before fidelity falls below a threshold; null if non-attenuating. */
export function relaysUntil(threshold: number, minPower: number): number | null {
  if (threshold <= 0 || threshold >= 1 || minPower <= 0 || minPower >= 1) return null;
  return Math.ceil(Math.log(threshold) / Math.log(1 - minPower));
}

// ---------------------------------------------------------------------------
// Phase exclusion
// ---------------------------------------------------------------------------

export type Phase = "constructing" | "committing";

/**
 * Why a sweep stopped short. The two causes are independent: one is relieved
 * by more resource, the other is not, and a report conflating them misleads.
 */
export type Quiescence = "exhausted" | "budget_bound" | "phase_bound" | "both";

export function classify(declined: number, phases: readonly Phase[]): Quiescence {
  const budgetBound = declined > 0;
  const phaseBound = phases.some((p) => p === "constructing");
  if (budgetBound && phaseBound) return "both";
  if (budgetBound) return "budget_bound";
  if (phaseBound) return "phase_bound";
  return "exhausted";
}

/** Fraction of instants spent constructing. */
export function constructionFraction(phases: readonly Phase[]): number {
  if (phases.length === 0) return 0;
  return phases.filter((p) => p === "constructing").length / phases.length;
}

/**
 * The commitment ceiling: `1 - φ`.
 *
 * Independent of the budget — an instant spent constructing is not available
 * for committing, and no amount of resource relaxes that.
 */
export function commitmentCeiling(phases: readonly Phase[]): number {
  return 1 - constructionFraction(phases);
}

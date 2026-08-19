/**
 * The TypeScript mirror must agree with the Rust on the same cases.
 *
 * Two of these encode counterexamples: exact optimality holds only for
 * divisible repertoires, and the shadow price must be the first excluded
 * candidate. Both boundaries were found by the Python validation and are
 * pinned on all three sides.
 */

import { describe, expect, it } from "vitest";

import {
  classify,
  commitmentCeiling,
  drift,
  fidelityBound,
  isDivisible,
  maxCommitments,
  origin,
  relay,
  relaysUntil,
  select,
  type Candidate,
  type Phase,
} from "./budget";

const c = (id: string, cost: number, gain: number): Candidate => ({ id, cost, gain });

/** Brute-force 0/1 knapsack, to check greedy against truth. */
function optimum(cands: Candidate[], budget: number): number {
  let best = 0;
  for (let mask = 0; mask < 1 << cands.length; mask++) {
    let cost = 0;
    let gain = 0;
    cands.forEach((cd, i) => {
      if (mask & (1 << i)) {
        cost += cd.cost;
        gain += cd.gain;
      }
    });
    if (cost <= budget + 1e-12 && gain > best) best = gain;
  }
  return best;
}

describe("selection under a bounded budget", () => {
  it("commits in density order until the budget is spent", () => {
    const s = select([c("lo", 1, 0.2), c("hi", 1, 0.9), c("mid", 1, 0.5)], {
      total: 2,
      floor: 0.5,
    });
    expect(s.committed).toEqual(["hi", "mid"]);
    expect(s.declined).toEqual(["lo"]);
    expect(s.totalGain).toBeCloseTo(1.4, 12);
  });

  it("declines by force of the budget, not by judgement", () => {
    const b = { total: 1, floor: 0.25 };
    expect(maxCommitments(b)).toBe(4);
    const cands = Array.from({ length: 10 }, (_, i) => c(`c${i}`, 0.25, 1.0));
    const s = select(cands, b);
    expect(s.committed).toHaveLength(4);
    expect(s.declined).toHaveLength(6);
  });

  it("never commits a non-positive gain", () => {
    const s = select([c("harmful", 1, -0.5), c("inert", 1, 0)], { total: 10, floor: 0.5 });
    expect(s.committed).toEqual([]);
  });

  it("is deterministic under ties", () => {
    const cands = [c("b", 1, 0.5), c("a", 1, 0.5), c("z", 1, 0.5)];
    const first = select(cands, { total: 2, floor: 0.5 });
    for (let i = 0; i < 10; i++) {
      expect(select(cands, { total: 2, floor: 0.5 }).committed).toEqual(first.committed);
    }
    expect(first.committed).toEqual(["a", "b"]);
  });
});

describe("the exact-optimality boundary", () => {
  it("is exactly optimal on a divisible repertoire", () => {
    const cands = [
      c("a", 0.25, 0.1),
      c("b", 0.25, 0.3),
      c("c", 0.25, 0.2),
      c("d", 0.25, 0.05),
    ];
    expect(isDivisible(cands)).toBe(true);
    const budget = 0.5;
    const s = select(cands, { total: budget, floor: 0.25 });
    expect(s.totalGain).toBeCloseTo(optimum(cands, budget), 9);
  });

  it("is NOT exactly optimal on indivisible bundles", () => {
    // The witness from the Python validation, pinned here and in Rust.
    const cands = [
      c("a", 0.5, 0.2),
      c("b", 0.5, 0.2),
      c("cc", 0.75, 0.3),
      c("d", 0.5, 0.4),
      c("e", 0.75, 0.6),
      c("f", 1.0, 0.8),
    ];
    // every cost is a multiple of the floor...
    for (const cd of cands) expect((cd.cost / 0.25) % 1).toBeCloseTo(0, 12);
    // ...but the repertoire is not divisible
    expect(isDivisible(cands)).toBe(false);

    const s = select(cands, { total: 1.75, floor: 0.25 });
    expect(s.totalGain).toBeCloseTo(1.2, 9);
    expect(optimum(cands, 1.75)).toBeCloseTo(1.4, 9);
    expect(s.totalGain).toBeLessThan(optimum(cands, 1.75));

    // the gap is still bounded by one candidate's gain
    const largest = Math.max(...cands.map((x) => x.gain));
    expect(optimum(cands, 1.75) - s.totalGain).toBeLessThanOrEqual(largest + 1e-9);
  });
});

describe("the shadow price", () => {
  it("is the first excluded candidate, not the last admitted", () => {
    const s = select([c("a", 1, 1.0), c("b", 1, 0.9), c("cc", 1, 0.8)], {
      total: 2,
      floor: 0.5,
    });
    expect(s.committed).toEqual(["a", "b"]);
    expect(s.shadowPrice).toBeCloseTo(0.8, 12); // excluded, not 0.9
  });

  it("falls as the budget widens", () => {
    const cands = [
      c("a", 1.0, 1.0),
      c("b", 0.5, 0.45),
      c("cc", 2.0, 1.6),
      c("d", 0.75, 0.5),
      c("e", 1.5, 0.9),
    ];
    let prev = Infinity;
    for (let steps = 1; steps <= 20; steps++) {
      const s = select(cands, { total: 0.5 * steps, floor: 0.25 });
      const price = s.shadowPrice ?? 0;
      expect(price).toBeLessThanOrEqual(prev + 1e-12);
      prev = price;
    }
  });

  it("is null once nothing is excluded", () => {
    const s = select([c("a", 1, 1)], { total: 100, floor: 0.25 });
    expect(s.shadowPrice).toBeNull();
    expect(s.declined).toEqual([]);
  });
});

describe("relay provenance", () => {
  it("accumulates drift multiplicatively", () => {
    let r = origin("account");
    for (const k of [0.2, 0.3, 0.5]) r = relay(r, k);
    expect(r.depth).toBe(3);
    expect(r.fidelity).toBeCloseTo(0.8 * 0.7 * 0.5, 12);
    expect(drift(r)).toBeCloseTo(1 - 0.8 * 0.7 * 0.5, 12);
  });

  it("drifts a chain of faithful relays", () => {
    let r = origin(null);
    for (let i = 0; i < 10; i++) r = relay(r, 0.2);
    // Python: 0.1074 after ten relays at k = 0.2
    expect(r.fidelity).toBeCloseTo(0.1073741824, 9);
    expect(drift(r)).toBeGreaterThan(0.89);
  });

  it("bounds fidelity from depth alone", () => {
    expect(fidelityBound(10, 0.2)).toBeCloseTo(0.1073741824, 9);
    expect(relaysUntil(0.5, 0.2)).toBe(4);
    expect(relaysUntil(0.5, 0)).toBeNull();
  });
});

describe("phase exclusion", () => {
  it("caps commitment independently of the budget", () => {
    const phases: Phase[] = Array.from({ length: 100 }, (_, i) =>
      i % 4 === 0 ? "constructing" : "committing",
    );
    expect(commitmentCeiling(phases)).toBeCloseTo(0.75, 12);

    // an enormous budget does not raise the ceiling
    expect(maxCommitments({ total: 1e6, floor: 0.25 })).toBeGreaterThan(1000);
    expect(commitmentCeiling(phases)).toBeCloseTo(0.75, 12);
  });

  it("distinguishes the two reasons a sweep stops short", () => {
    const none: Phase[] = ["committing"];
    const some: Phase[] = ["constructing", "committing"];
    expect(classify(0, none)).toBe("exhausted");
    expect(classify(5, none)).toBe("budget_bound");
    expect(classify(0, some)).toBe("phase_bound");
    expect(classify(5, some)).toBe("both");
  });
});

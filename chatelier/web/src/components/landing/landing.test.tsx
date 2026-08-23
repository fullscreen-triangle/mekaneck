/**
 * The landing page states results, so it must not state them wrongly.
 *
 * These are not layout tests. The page describes a null result, and the
 * failure mode that matters is a page that keeps its confident prose while
 * the numbers behind it have changed or gone missing. Each test pins one way
 * that could happen.
 */

import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../shell/App";
import { Landing } from "./Landing";

/** The shape the chart builder emits, with values from the 86-night record. */
const RECORD = {
  meta: { n_nights: 86, n_epochs: 8706 },
  floor_test: {
    stage_level: {
      exactly_zero: 9,
      n: 321,
      curve: { intercept: -0.0999, intercept_sd: 0.1784, sign_stable: false },
    },
    intraday: { zero_fraction: 0.1849, quantum_fraction: 0.654 },
  },
  transitions: { eta: 0.0496 },
};

function mockFetch(body: unknown, ok = true) {
  vi.stubGlobal(
    "fetch",
    vi.fn(() => Promise.resolve({ ok, status: ok ? 200 : 404, json: () => Promise.resolve(body) })),
  );
}

afterEach(() => vi.unstubAllGlobals());

describe("landing page", () => {
  it("reports the floor estimate with its spread, never bare", async () => {
    mockFetch(RECORD);
    const { container } = render(<Landing />);

    // The stage-level intercept flips sign with the ordering of the record.
    // Printed alone it reads as a measurement; it is not one, so the spread
    // has to travel with it wherever it appears.
    await waitFor(() => {
      expect(container.textContent).toContain("-0.100 ± 0.178");
    });
  });

  it("draws its figures from the record rather than from prose", async () => {
    mockFetch({
      ...RECORD,
      meta: { n_nights: 12, n_epochs: 500 },
      transitions: { eta: 0.4242 },
    });
    const { container } = render(<Landing />);

    await waitFor(() => expect(container.textContent).toContain("0.4242"));
    // If the sentences carried hardcoded numbers, the 86-night defaults would
    // still be here alongside the ones actually supplied.
    expect(container.textContent).toContain("12 nights");
    expect(container.textContent).not.toContain("0.0496");
  });

  it("falls back to qualitative wording when the record is absent", async () => {
    mockFetch(null, false);
    const { container } = render(<Landing />);

    // A missing file must not produce a number that nothing computed.
    await waitFor(() => expect(container.textContent).toContain("A calculus for inquiry"));
    expect(container.textContent).toContain("spread wider than the estimate");
    expect(container.textContent).not.toContain("±");
  });

  it("keeps the identity caveat attached to the perfect-agreement figure", async () => {
    mockFetch(RECORD);
    render(<Landing />);

    // r = 1.000 is the single most misreadable number in the framework.
    // Wherever it appears it must be marked as an identity.
    await waitFor(() => {
      const el = screen.getByText(/telescoping obstruction/i).parentElement;
      expect(el?.textContent).toMatch(/identity, not a finding/i);
    });
  });

  it("presents the law table under the estimator that makes it meaningful", async () => {
    mockFetch(RECORD);
    const { container } = render(<Landing />);

    // The comparison is only informative type-averaged; an unlabelled table
    // invites the reader to take it as a result under any estimator.
    await waitFor(() => expect(container.textContent).toContain("0.988"));
    expect(container.textContent).toMatch(/type-averaged/i);
  });
});

describe("deployed instance", () => {
  /**
   * A deployed page cannot pair with a local binary: the browser blocks a
   * ws:// connection to loopback from an https origin. Showing the usual
   * "run `mekaneck serve`" prompt there sends the reader after a fault that
   * is not theirs and that no action of theirs can fix.
   */
  it("says why pairing is impossible over https rather than prompting for a token", () => {
    const orig = window.location;
    // jsdom's location is read-only; replace it for the duration of the test.
    Object.defineProperty(window, "location", {
      value: { ...orig, protocol: "https:", hash: "" },
      writable: true,
      configurable: true,
    });

    try {
      const { container } = render(<App />);
      // It must explain the mixed-content block and route the reader to the
      // local path, not offer a token field that cannot succeed.
      expect(container.textContent).toMatch(/mixed content/i);
      expect(container.textContent).toMatch(/run the tool locally/i);
      expect(container.querySelector('input[placeholder*="token"]')).toBeNull();
    } finally {
      Object.defineProperty(window, "location", {
        value: orig,
        writable: true,
        configurable: true,
      });
    }
  });

  it("offers a working token field when served locally", () => {
    const { container } = render(<App />);
    // http origin: pairing is possible, so the field must actually be there.
    expect(container.textContent).toMatch(/mekaneck serve/i);
    expect(container.querySelector('input[placeholder*="token"]')).not.toBeNull();
  });
});

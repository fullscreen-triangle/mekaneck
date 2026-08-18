import { describe, expect, it } from "vitest";

import { completions, markers } from "./monarch";

describe("editor markers", () => {
  const substrate =
    "substrate Osc { receivers : r(); observable : o(); events : e(); floor : asymptotic(); }";
  const triad = [
    "catalyst a : f() independent b, c;",
    "catalyst b : g() independent a, c;",
    "catalyst c : h() independent a, b;",
  ].join("\n");
  const good = `${substrate}\n${triad}\nlet x = seek t() excluding rest() via (a, b, c) until closure;\nreport x;`;

  it("produces none for a well-formed program", () => {
    expect(markers(good, { Osc: 12.5 })).toHaveLength(0);
  });

  it("marks a real span, never a zero-width one", () => {
    const bad = good.replace("excluding rest() ", "");
    const m = markers(bad, { Osc: 12.5 });
    expect(m).toHaveLength(1);
    expect(m[0].severity).toBe(8);
    // Monaco renders nothing for a zero-width marker.
    expect(m[0].endColumn).toBeGreaterThan(m[0].startColumn);
  });

  it("uses warning severity for an unchecked floor", () => {
    const m = markers(good, {});
    expect(m).toHaveLength(1);
    expect(m[0].severity).toBe(4);
  });
});

describe("completions teach a shape the checker accepts", () => {
  it("the seek snippet includes the mandatory exclusion clause", () => {
    const seek = completions.find((c) => c.label === "seek")!;
    expect(seek.insertText).toContain("excluding");
    expect(seek.insertText).toContain("until       closure");
  });

  it("the catalyst snippet offers three, mutually independent", () => {
    const triad = completions.find((c) => c.label === "catalyst-triad")!;
    const lines = triad.insertText.split("\n");
    expect(lines).toHaveLength(3);
    for (const l of lines) expect(l).toContain("independent");
  });

  it("the substrate snippet defaults to a falsifiable floor estimator", () => {
    const s = completions.find((c) => c.label === "substrate")!;
    expect(s.insertText).toContain("asymptotic_separation()");
    expect(s.insertText).not.toContain("sample_minimum");
  });
});

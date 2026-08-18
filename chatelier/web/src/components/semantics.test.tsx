/**
 * The interface must not lose what the protocol carries.
 *
 * These are not rendering tests. Each asserts a claim from the papers that an
 * interface can silently violate: presenting an algebraic identity as a
 * finding, collapsing a contested closure to a single answer, or showing a
 * floor from an unfalsifiable estimator as though it were evidence.
 */

import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { BindingResult, LawRow, ReceiverFloor, SeparationReport } from "../connection/protocol";
import { LawComparison } from "./charts/LawComparison";
import { FloorPanel } from "./charts/FloorPanel";
import { SeparationGauge } from "./charts/SeparationGauge";
import { OutcomePanel } from "./panels/OutcomePanel";
import { summariseBinding } from "../state/store";

const laws: LawRow[] = [
  {
    law: "multiplicative",
    estimation: "instance_specific",
    evidential: false,
    max_discrepancy: 2.22e-16,
    pearson_r: 1.0,
    rmse: 0.0,
  },
  {
    law: "multiplicative",
    estimation: "type_averaged",
    evidential: true,
    max_discrepancy: 0.137,
    pearson_r: 0.988,
    rmse: 0.019,
  },
  {
    law: "additive",
    estimation: "type_averaged",
    evidential: true,
    max_discrepancy: 0.29,
    pearson_r: 0.841,
    rmse: 0.169,
  },
];

describe("an algebraic identity is never presented as a finding", () => {
  it("segregates instance-specific rows and states why", () => {
    render(
      <LawComparison
        laws={laws}
        selectedLaw={null}
        onSelectLaw={() => {}}
        showNonEvidential
        onToggleNonEvidential={() => {}}
      />,
    );
    // The perfect fit is present, but explained. The phrase appears both on
    // the disclosure control and in the caveat, which is intended: a reader
    // who never expands the section still sees the warning.
    expect(screen.getAllByText(/algebraic identit/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/is not evidence/i)).toBeTruthy();
    expect(screen.getByText(/1\.000/)).toBeTruthy();
  });

  it("ranks best-fit only among rows that can carry evidence", () => {
    // r = 1.000 is the largest value present, but it is an identity; the
    // ranking must not crown it.
    const { container } = render(
      <LawComparison
        laws={laws}
        selectedLaw={null}
        onSelectLaw={() => {}}
        showNonEvidential={false}
        onToggleNonEvidential={() => {}}
      />,
    );
    // with identities collapsed, only type-averaged rows are listed
    expect(container.textContent).toContain("0.988");
    expect(container.textContent).not.toContain("1.000");
  });

  it("renders an undefined correlation as n/a rather than zero", () => {
    const undefinedR: LawRow[] = [
      { ...laws[1], pearson_r: null, rmse: null },
    ];
    render(
      <LawComparison
        laws={undefinedR}
        selectedLaw={null}
        onSelectLaw={() => {}}
        showNonEvidential={false}
        onToggleNonEvidential={() => {}}
      />,
    );
    expect(screen.getByText("n/a")).toBeTruthy();
  });
});

describe("a contested closure is a result, not a failure", () => {
  const declined: BindingResult = {
    name: "regime",
    outcome: { outcome: "declined", cells: ["high", "mixed"] },
    record: 2,
    trace: [
      { catalyst: "spectral", cell: "high", record: 1 },
      { catalyst: "phase", cell: "mixed", record: 2 },
    ],
  };

  it("shows every reached cell, not a selected one", () => {
    render(<OutcomePanel bindings={[declined]} />);
    expect(screen.getByText("high")).toBeTruthy();
    expect(screen.getByText("mixed")).toBeTruthy();
    expect(screen.getByText(/CONTESTED CLOSURE/)).toBeTruthy();
  });

  it("attributes each cell to the catalysts that reached it", () => {
    const { container } = render(<OutcomePanel bindings={[declined]} />);
    expect(container.textContent).toContain("via spectral");
    expect(container.textContent).toContain("via phase");
  });

  it("says it is a normal termination", () => {
    render(<OutcomePanel bindings={[declined]} />);
    expect(screen.getByText(/normal termination, not a failure/i)).toBeTruthy();
  });

  it("logs a declination under its own kind, never as an error", () => {
    const line = summariseBinding(declined);
    expect(line.kind).toBe("contested");
    expect(line.kind).not.toBe("error");
    expect(line.text).toContain("high");
    expect(line.text).toContain("mixed");
  });

  it("logs a resolution as such", () => {
    const line = summariseBinding({
      name: "regime",
      outcome: { outcome: "resolved", cell: "high" },
      record: 1,
      trace: [{ catalyst: "spectral", cell: "high", record: 1 }],
    });
    expect(line.kind).toBe("ok");
  });
});

describe("floor estimates carry their falsifiability", () => {
  const receivers: ReceiverFloor[] = [
    {
      receiver: "rec1",
      floor: 10.0,
      estimator: "asymptotic",
      falsifiable: true,
      supports_positive_floor: true,
    },
    {
      receiver: "rec2",
      floor: 10.0,
      estimator: "samplminimum",
      falsifiable: false,
      supports_positive_floor: false,
    },
  ];

  it("warns when an estimator cannot return a non-positive value", () => {
    render(<FloorPanel receivers={receivers} selected={null} onSelect={() => {}} />);
    expect(screen.getByText(/positivity is not evidence/i)).toBeTruthy();
  });

  it("marks a receiver whose estimate does not support a positive floor", () => {
    const { container } = render(
      <FloorPanel receivers={receivers} selected={null} onSelect={() => {}} />,
    );
    expect(container.textContent).toContain("!");
    expect(container.textContent).toContain("✓");
  });

  it("says nothing about falsifiability when every estimator can fail", () => {
    render(
      <FloorPanel receivers={[receivers[0]]} selected={null} onSelect={() => {}} />,
    );
    expect(screen.queryByText(/positivity is not evidence/i)).toBeNull();
  });
});

describe("separation gates how a law comparison may be read", () => {
  const base: SeparationReport = {
    eta: 0.97,
    between: 0.02,
    within: 0.0006,
    n_types: 4,
    n_events: 800,
    informative: true,
  };

  it("is silent when the binding discriminates", () => {
    render(<SeparationGauge separation={base} />);
    expect(screen.queryByText(/cannot adjudicate/i)).toBeNull();
  });

  it("warns that a correlation below threshold is not evidence of typing", () => {
    render(
      <SeparationGauge
        separation={{ ...base, eta: 1.2e-4, informative: false }}
      />,
    );
    expect(screen.getByText(/cannot adjudicate the typing/i)).toBeTruthy();
    expect(screen.getByText(/cascade-length variation/i)).toBeTruthy();
  });

  it("renders a very small eta without collapsing it to zero", () => {
    render(
      <SeparationGauge
        separation={{ ...base, eta: 1.2e-4, informative: false }}
      />,
    );
    expect(screen.getByText(/1\.2e-4/)).toBeTruthy();
  });
});

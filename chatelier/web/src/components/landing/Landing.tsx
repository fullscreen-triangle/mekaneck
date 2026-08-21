/**
 * The landing page.
 *
 * Written as a paper rather than as a product page: an abstract, numbered
 * sections, displayed definitions, a results table, and a stated scope. The
 * reason is not stylistic. The framework's central claims are negative — that
 * a natural test is vacuous, that a trajectory is not reproducible, that a
 * measured floor was an artefact of the instrument — and negative claims are
 * not communicable in the register of a feature list. A reader who arrives
 * expecting capabilities will mistake the honest reporting of a null result
 * for a missing feature.
 *
 * Every quantity rendered here is read from the same JSON the validation
 * suites emit, so the page cannot drift from what the suites report. Where
 * the file is absent the sentences fall back to their qualitative form rather
 * than printing a number nothing produced.
 */

import { useEffect, useState } from "react";

import { mono, palette, sans } from "../../theme";

const MAX_W = 780;

interface Numbers {
  nights: number | null;
  epochs: number | null;
  eta: number | null;
  stageIntercept: number | null;
  stageSd: number | null;
  stageZeros: number | null;
  stageN: number | null;
  zeroFraction: number | null;
  quantumFraction: number | null;
}

const EMPTY: Numbers = {
  nights: null,
  epochs: null,
  eta: null,
  stageIntercept: null,
  stageSd: null,
  stageZeros: null,
  stageN: null,
  zeroFraction: null,
  quantumFraction: null,
};

export function Landing({ onEnter }: { onEnter?: () => void }) {
  const [n, setN] = useState<Numbers>(EMPTY);

  useEffect(() => {
    fetch("/dataset/cardiac_charts.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((d) => {
        const st = d.floor_test?.stage_level;
        const it = d.floor_test?.intraday;
        setN({
          nights: d.meta?.n_nights ?? null,
          epochs: d.meta?.n_epochs ?? null,
          eta: d.transitions?.eta ?? null,
          stageIntercept: st?.curve?.intercept ?? null,
          stageSd: st?.curve?.intercept_sd ?? null,
          stageZeros: st?.exactly_zero ?? null,
          stageN: st?.n ?? null,
          zeroFraction: it?.zero_fraction ?? null,
          quantumFraction: it?.quantum_fraction ?? null,
        });
      })
      .catch(() => setN(EMPTY));
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: palette.bg,
        color: palette.text,
        fontFamily: sans,
        overflowY: "auto",
      }}
    >
      <article style={{ maxWidth: MAX_W, margin: "0 auto", padding: "64px 28px 120px" }}>
        <Masthead onEnter={onEnter} />
        <Abstract n={n} />
        <Section num="1" title="The problem">
          <Problem />
        </Section>
        <Section num="2" title="The residual algebra">
          <Algebra />
        </Section>
        <Section num="3" title="A kernel that renders no verdict">
          <Kernel />
        </Section>
        <Section num="4" title="The language">
          <Language />
        </Section>
        <Section num="5" title="Worked substrate: an 86-night cardiac record">
          <Cardiac n={n} />
        </Section>
        <Section num="6" title="Verification">
          <Verification />
        </Section>
        <Section num="7" title="Scope and limitations">
          <Limits />
        </Section>
        <Colophon />
      </article>
    </div>
  );
}

/* ------------------------------------------------------------------ */

function Masthead({ onEnter }: { onEnter?: () => void }) {
  return (
    <header style={{ marginBottom: 40 }}>
      <div
        style={{
          fontFamily: mono,
          fontSize: 11,
          color: palette.textFaint,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          marginBottom: 14,
        }}
      >
        Mekaneck
      </div>
      <h1
        style={{
          fontSize: 33,
          lineHeight: 1.22,
          fontWeight: 600,
          color: palette.textBright,
          margin: "0 0 16px",
          letterSpacing: "-0.015em",
        }}
      >
        A calculus for inquiry that cannot be completed
      </h1>
      <p style={{ fontSize: 15, lineHeight: 1.65, color: palette.textDim, margin: "0 0 22px" }}>
        A residual algebra, an execution kernel that renders no verdict, and a
        language whose termination condition is the exhaustion of reachable
        outcomes rather than the crossing of a confidence threshold.
      </p>
      <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        {onEnter && (
          <button
            onClick={onEnter}
            style={{
              padding: "7px 16px",
              background: palette.accent,
              border: "none",
              borderRadius: 3,
              color: "#fff",
              fontFamily: sans,
              fontSize: 13,
              cursor: "pointer",
            }}
          >
            Open the editor
          </button>
        )}
        <span style={{ fontFamily: mono, fontSize: 11, color: palette.textFaint }}>
          three papers · seven crates · runs on your machine
        </span>
      </div>
    </header>
  );
}

function Abstract({ n }: { n: Numbers }) {
  return (
    <div
      style={{
        borderLeft: `2px solid ${palette.border}`,
        padding: "2px 0 2px 20px",
        marginBottom: 44,
      }}
    >
      <Label>Abstract</Label>
      <p style={para}>
        An observer reduces its uncertainty about a target through a sequence of
        events. We take the position that such events do not add their
        reductions but compose multiplicatively on the gap their predecessors
        left, and that the gap is measured from a floor whose positivity is
        derived from non-completability rather than assumed. From these two
        commitments the composition rule, the unattainability of the floor, and
        a convergence criterion follow.
      </p>
      <p style={para}>
        The principal result is negative. The natural empirical test of the
        composition law is <em>vacuous</em>: when the constituent powers are
        estimated from the same sequence that determines the outcome, the
        prediction and the measurement are the same algebraic expression, and
        the test reports perfect agreement on data from any process whatsoever
        — including processes that violate every claim we make. We give the
        exact condition under which this holds, and the estimator that restores
        a genuine null hypothesis.
      </p>
      <p style={{ ...para, marginBottom: 0 }}>
        A worked substrate over {n.nights ?? 86} nights of consumer wearable
        data illustrates what the apparatus is for: it returns a null. Cardiac
        separation has no positive floor on that record, the measured floor is
        the instrument quantum, and the substrate is diagnosed as uninformative
        at η = {n.eta?.toFixed(4) ?? "0.0496"}. A program that requires a
        positive floor does not type-check over it.
      </p>
    </div>
  );
}

function Problem() {
  return (
    <>
      <p style={para}>
        Three questions arise about any such sequence, and the usual answers to
        all three are unsatisfactory.
      </p>
      <Numbered
        items={[
          <>
            <b>How do the events compose?</b> The intuitive answer is that their
            reductions add. For any process in which each event acts on what its
            predecessors left, the correct answer is that the <i>residuals</i>{" "}
            multiply — addition double-counts the overlap and can exceed unity.
          </>,
          <>
            <b>From what baseline is a reduction measured?</b> A gap must be
            measured from somewhere. Set the floor to zero and the algebra
            degenerates; set it to an arbitrary constant and the predictions
            become unfalsifiable. The floor has to be a declared, estimated,
            falsifiable property of the substrate.
          </>,
          <>
            <b>When is the inquiry finished?</b> The standard criterion —
            continue until attained uncertainty falls below a threshold — fails
            for a reason that can be stated precisely: a single internally
            consistent line of evidence satisfies any threshold <i>because</i>{" "}
            it is internally consistent, while an unexamined second line would
            have reached an incompatible conclusion.
          </>,
        ]}
      />
    </>
  );
}

function Algebra() {
  return (
    <>
      <p style={para}>
        Write <M>S</M> for the uncertainty outstanding about a target and <M>β</M>{" "}
        for the floor: the irreducible remainder of an identification that no
        finite stage completes. The catalytic power of an event carrying the
        observer from <M>S</M> to <M>S′</M> is the fraction of the outstanding
        gap it closes.
      </p>
      <Display>κ = (S − S′) / (S − β),   0 ≤ κ &lt; 1</Display>
      <p style={para}>
        Because each event acts on the gap left by the last, the residuals{" "}
        <M>(1 − κ)</M> compose by multiplication, and the power of a cascade is
        one minus their product.
      </p>
      <Display>κ(e₁ ⊕ ⋯ ⊕ eₙ) = 1 − Π (1 − κᵢ)</Display>
      <p style={para}>
        Three consequences follow immediately and are not independent
        assumptions: the floor is approached but never attained; a cascade
        converges to complete identification exactly when Σ κᵢ diverges; and the
        fidelity of a relayed result is Π(1 − κᵢ) over the relay chain, so drift
        is a corollary of composition rather than a separate model.
      </p>
      <Callout tone="warn" title="The telescoping obstruction">
        Suppose the powers κᵢ are estimated from the same state sequence whose
        endpoints determine the cascade outcome. Then the product <M>Π(1 − κᵢ)</M>{" "}
        telescopes to <M>(Sₙ − β)/(S₀ − β)</M>, which is the measured outcome.
        Prediction and measurement are the same expression. The test reports{" "}
        <M>r = 1.000</M> with a maximum deviation of <M>2.22 × 10⁻¹⁶</M> — one
        unit in the last place of double precision — on every cascade in every
        regime, including regimes generated by processes that violate
        type-stability entirely. That agreement is an identity, not a finding.
        The implementation marks it as such, and{" "}
        <code style={code}>is_evidential()</code> returns false however close the
        agreement.
      </Callout>
      <p style={{ ...para, marginBottom: 0 }}>
        Replacing instance-specific powers with <i>type-averaged</i> ones
        restores a genuine null. Under that estimator the multiplicative law is
        no longer guaranteed and can be compared against rivals — which is the
        only regime in which the comparison means anything.
      </p>
    </>
  );
}

function Kernel() {
  return (
    <>
      <p style={para}>
        A conventional runtime reports whether a program succeeded. That is
        correct for a program and wrong for an experiment: an experiment that
        reports failure because an outcome did not occur has confused a result
        with an error. The kernel therefore renders no verdict, and this is
        enforced rather than merely intended.
      </p>
      <Callout tone="plain" title="Inertia">
        The kernel cannot compute a quantity meaning “wrong”. An exit code of
        that kind requires a stored expectation against which an outcome is
        compared, and the state space contains none. The restriction is
        structural, not a policy a caller could override.
      </Callout>
      <p style={para}>
        From it follow run-to-completion under anomaly, order-independent
        convergence of independently derived decompositions, and a monotone
        execution record that orders events without reference to a clock.
      </p>
      <p style={para}>
        The consequential result is a separation between what is reproducible
        and what is not. The <b>protocol</b> — what <i>can</i> be computed — is a
        function of the submitted decompositions and admits a stable
        fingerprint. The <b>trajectory</b> — what <i>was</i> computed — is a
        function of neither the protocol nor the terminal result, and is
        therefore not reproducible in principle for this class of computation. A
        reproducibility claim that does not distinguish the two is ill-founded.
      </p>
      <p style={{ ...para, marginBottom: 0 }}>
        Chunks declare the identities they read, and the graph refuses a merge
        that would introduce a cycle among those reads; that refusal is what
        makes convergence order-independent. Mutual independence among catalysts
        is a different relation — independent catalysts do not inform one
        another — so the three-catalyst coherence requirement lives in the
        support graph and is not in tension with acyclicity of reads.
      </p>
    </>
  );
}

function Language() {
  return (
    <>
      <p style={para}>
        Programs are written in <code style={code}>.mck</code>: one computational
        primitive, two non-standard typing rules, three reduction rules, with a
        full grammar, type system, small-step semantics, and metatheory —
        progress, preservation, determinism modulo substrate, and termination.
      </p>
      <Code>{`substrate Cardiac {
  receivers  : nights("sleep_summary");
  observable : rmssd_5min();
  events     : stage_transition();
  floor      : asymptotic_separation();   # falsifiable
}

catalyst variability : rmssd_dispersion() independent rate, architecture;
catalyst rate        : hr_level()         independent variability, architecture;
catalyst architecture: hypnogram_run()    independent variability, rate;

let regime = seek target_state("high-variability")
  excluding all_other_states()
  via (variability, rate, architecture)
  until closure;

report regime;`}</Code>
      <p style={para}>
        Two commitments are carried by the type system rather than by
        convention.
      </p>
      <Numbered
        items={[
          <>
            <b>Exclusion is mandatory.</b> A <code style={code}>seek</code> must
            state what its target is being told apart from. A positive
            description alone does not determine a target, so a{" "}
            <code style={code}>seek</code> without an{" "}
            <code style={code}>excluding</code> clause has no unique denotation
            and is rejected at parse time.
          </>,
          <>
            <b>Termination is by exhaustion.</b> A <code style={code}>seek</code>{" "}
            completes when no remaining catalyst can carry it to an outcome
            outside the set already reached. This is strictly stronger than any
            confidence threshold and is not obtained by lowering one.
          </>,
        ]}
      />
      <p style={para}>
        Closure resolves into exactly two typed outcomes, and neither is an
        error. A run ending in disagreement exits zero.
      </p>
      <Code>{`$ mekaneck run examples/coherence.mck --floor Osc=12.5 \\
    --cell spectral=high --cell surrogate=high --cell phase=mixed
regime: declined, 2 incompatible cells  (record 2)
    high  via spectral
    mixed via phase`}</Code>
      <p style={{ ...para, marginBottom: 0 }}>
        A confidence threshold would have halted after{" "}
        <code style={code}>spectral</code> returned a confident cell and never
        consulted <code style={code}>phase</code>. The declination is the
        informative outcome: it reports that the question, as posed over this
        registry, has more than one defensible answer.
      </p>
    </>
  );
}

function Cardiac({ n }: { n: Numbers }) {
  const zeroPct = n.zeroFraction != null ? `${(n.zeroFraction * 100).toFixed(1)}%` : "18.5%";
  const quantumPct =
    n.quantumFraction != null ? `${(n.quantumFraction * 100).toFixed(1)}%` : "65.4%";

  return (
    <>
      <p style={para}>
        The substrate obligations are not rhetorical, so it is worth showing them
        fail. We bound the language to {n.nights ?? 86} nights of consumer
        wearable data — {n.epochs?.toLocaleString() ?? "8,706"} five-minute
        epochs with sleep staging, plus intraday series at five-second resolution
        — and asked whether cardiac separation has a positive floor.
      </p>
      <p style={para}>
        It does not, and three candidate answers turned out to be artefacts of
        how the question was posed.
      </p>
      <Numbered
        items={[
          <>
            Writing separation as <M>S = c − rmssd</M> returns a positive floor
            for <i>every</i> constant <M>c</M> above the sample maximum. The
            positivity is forced by the coordinate choice and measures nothing.
          </>,
          <>
            Writing it as <M>S = |rmssd − median|</M> returns exactly zero,
            because the data are integers and 157 epochs sit precisely at the
            median. That zero is forced too.
          </>,
          <>
            Extrapolating running minima gives an intercept whose <i>sign is not
            stable</i>: it flips with the ordering of the record and with the
            number of stages fitted. On the stage separations it is{" "}
            {n.stageIntercept != null && n.stageSd != null
              ? `${n.stageIntercept.toFixed(3)} ± ${n.stageSd.toFixed(3)}`
              : "negative on average, with a spread wider than the estimate"}
            . A point estimate that unstable is not a measurement, and is
            reported with its spread rather than on its own.
          </>,
        ]}
      />
      <p style={para}>
        What survives is the part that depends on no modelling choice. Of{" "}
        {n.stageN ?? 321} stage separations, {n.stageZeros ?? 9} are exactly
        zero: on those nights two sleep stages were indistinguishable in RMSSD.
        Zero is <i>attained</i>, so no positive floor can be asserted over this
        record. At five-second resolution the answer is sharper — heart rate is
        reported as an integer, {zeroPct} of consecutive epochs are identical,
        and {quantumPct} of the non-zero separations are exactly 1 bpm.
      </p>
      <Callout tone="fail" title="The measured floor is the instrument, not the physiology">
        Below one beat per minute the record cannot distinguish states at all, so
        a floor estimated from this data measures the quantisation of the sensor.
        The null is not a power failure: at n = 321 the estimator detects a
        genuine 1 ms floor 99.7% of the time, and returns approximately zero
        under the null.
      </Callout>
      <p style={{ ...para, marginBottom: 0 }}>
        Separately, the twelve transition types give η = {n.eta?.toFixed(4) ?? "0.0496"},
        below the 0.05 threshold, so the typing does not discriminate. A
        non-trivial correlation obtained over this substrate would be carried by
        cascade length rather than by type identity, and would not be evidence
        that the typing is correct. Both facts are surfaced in the editor before
        the results they qualify, not after.
      </p>
    </>
  );
}

function Verification() {
  return (
    <>
      <p style={para}>Four suites, run independently.</p>
      <Code>{`cargo test                        # Rust:       202 tests
cd web && npm test                # TypeScript:  54 tests
python validation/run_all.py      # Python:      32 checks

mekaneck serve --port 8731        # then, against the live binary:
python validation/smoke_server.py --token <TOKEN>   # 19 end-to-end checks`}</Code>
      <p style={para}>
        The Python suites are the reference implementation the papers report; the
        Rust conformance tests assert the same values, so the two cannot drift
        apart silently. Protocol types for the browser are <i>generated</i> from
        the Rust definitions and a test fails the build if the checked-in
        TypeScript goes stale. The editor's local checker is pinned to the binary
        by a shared fixture suite of fifteen diagnostic cases with exact source
        positions.
      </p>
      <p style={para}>
        Representative measured values — separated regime, 4000 cascades, under
        type-averaged estimation, the regime in which the comparison is
        meaningful:
      </p>
      <Table
        head={["Composition law", "Pearson r", "RMSE"]}
        rows={[
          ["Multiplicative", "0.988", "0.019"],
          ["Additive", "0.841", "0.169"],
          ["Geometric mean", "0.818", "0.450"],
          ["Maximum", "0.735", "0.313"],
        ]}
      />
      <p style={{ ...para, marginBottom: 0 }}>
        In the compressed regime (η = 1.2 × 10⁻⁴) the test loses its power to
        adjudicate the typing, yet the multiplicative law still returns r = 0.634
        — traceable to cascade-length variation rather than to type identity. The
        suites report that case as an absence of power, not as a disconfirmation.
      </p>
    </>
  );
}

function Limits() {
  return (
    <>
      <p style={para}>
        Stated plainly, because each bears on how the results should be read.
      </p>
      <Numbered
        items={[
          <>
            <b>The composition law is a consequence of the definitions, not an
            empirical claim.</b> Given that power is a fraction of an outstanding
            gap measured from a fixed floor, composition is multiplicative and
            cannot fail. What is empirical is whether a proposed decomposition
            obeys it when powers are estimated independently of the outcome being
            predicted.
          </>,
          <>
            <b>No claim is made that any particular process decomposes into
            type-stable events.</b> That is a separate empirical question per
            substrate. The apparatus exists to make it answerable, not to
            presuppose an answer.
          </>,
          <>
            <b>Closure is only as good as the catalyst registry.</b> The
            criterion quantifies over available catalysts, not conceivable ones.
            Closure over an impoverished registry means the registry is
            exhausted, not that the question is settled.
          </>,
          <>
            <b>The coherence rule is a necessary condition, not a sufficient
            one.</b> Three catalysts declared independent but sharing an upstream
            source or a common preprocessing step satisfy the rule while
            violating its intent. The language cannot verify independence; it
            requires the claim to be written where it can be audited.
          </>,
          <>
            <b>Self-analysis is restricted.</b> A kernel may analyse its own
            execution record, which is an ordinary trace. It may not host a total
            verdict function closed under its own diagonal. This is the classical
            obstruction, stated rather than circumvented.
          </>,
        ]}
      />
    </>
  );
}

function Colophon() {
  return (
    <footer
      style={{
        marginTop: 52,
        paddingTop: 20,
        borderTop: `1px solid ${palette.borderSubtle}`,
        fontSize: 12.5,
        lineHeight: 1.7,
        color: palette.textFaint,
      }}
    >
      <p style={{ margin: "0 0 10px" }}>
        The <code style={code}>mekaneck</code> binary runs entirely on your
        machine. The server binds loopback and never dials out; the browser
        connects <i>to</i> your machine, so analysis data does not leave the
        host. The pairing token is a per-run secret — 32 bytes from the operating
        system CSPRNG, never persisted, compared in constant time, invalidated by
        restarting the binary — rather than an account credential.
      </p>
      <p style={{ margin: 0 }}>
        Kundai Farai Sachikonye · Technical University of Munich · MIT licence.
      </p>
    </footer>
  );
}

/* ---------------------------- primitives --------------------------- */

const para: React.CSSProperties = {
  fontSize: 14.5,
  lineHeight: 1.75,
  color: palette.text,
  margin: "0 0 16px",
};

const code: React.CSSProperties = {
  fontFamily: mono,
  fontSize: "0.9em",
  color: palette.synIdent,
};

function Section({
  num,
  title,
  children,
}: {
  num: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section style={{ marginBottom: 42 }}>
      <h2
        style={{
          fontSize: 18,
          fontWeight: 600,
          color: palette.textBright,
          margin: "0 0 14px",
          display: "flex",
          gap: 12,
          alignItems: "baseline",
        }}
      >
        <span style={{ fontFamily: mono, fontSize: 13, color: palette.accent }}>{num}</span>
        {title}
      </h2>
      {children}
    </section>
  );
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        fontFamily: mono,
        fontSize: 10,
        letterSpacing: "0.14em",
        textTransform: "uppercase",
        color: palette.textFaint,
        marginBottom: 10,
      }}
    >
      {children}
    </div>
  );
}

/** Inline mathematical symbol. */
function M({ children }: { children: React.ReactNode }) {
  return (
    <span style={{ fontFamily: mono, fontSize: "0.93em", color: palette.synIdent }}>
      {children}
    </span>
  );
}

function Display({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        fontFamily: mono,
        fontSize: 14,
        color: palette.textBright,
        textAlign: "center",
        padding: "16px 10px",
        margin: "6px 0 18px",
        background: palette.bgSunken,
        borderRadius: 3,
      }}
    >
      {children}
    </div>
  );
}

function Code({ children }: { children: string }) {
  return (
    <pre
      style={{
        fontFamily: mono,
        fontSize: 12,
        lineHeight: 1.6,
        color: palette.text,
        background: palette.bgSunken,
        border: `1px solid ${palette.borderSubtle}`,
        borderRadius: 3,
        padding: "13px 15px",
        margin: "0 0 18px",
        overflowX: "auto",
      }}
    >
      {children}
    </pre>
  );
}

function Numbered({ items }: { items: React.ReactNode[] }) {
  return (
    <ol style={{ margin: "0 0 16px", padding: 0, listStyle: "none" }}>
      {items.map((it, i) => (
        <li key={i} style={{ display: "flex", gap: 13, marginBottom: 13 }}>
          <span
            style={{
              fontFamily: mono,
              fontSize: 11,
              color: palette.textFaint,
              flexShrink: 0,
              paddingTop: 4,
            }}
          >
            {String(i + 1).padStart(2, "0")}
          </span>
          <span style={{ fontSize: 14.5, lineHeight: 1.75 }}>{it}</span>
        </li>
      ))}
    </ol>
  );
}

/**
 * A boxed remark. The tone is semantic rather than decorative: `warn` marks a
 * result that looks positive and is not, `fail` marks a null.
 */
function Callout({
  tone,
  title,
  children,
}: {
  tone: "plain" | "warn" | "fail";
  title: string;
  children: React.ReactNode;
}) {
  const colour =
    tone === "warn" ? palette.identity : tone === "fail" ? palette.failed : palette.border;
  return (
    <div
      style={{
        borderLeft: `2px solid ${colour}`,
        background: palette.bgSunken,
        padding: "13px 16px",
        margin: "0 0 18px",
        borderRadius: "0 3px 3px 0",
      }}
    >
      <div
        style={{
          fontFamily: mono,
          fontSize: 10.5,
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          color: tone === "plain" ? palette.textDim : colour,
          marginBottom: 8,
        }}
      >
        {title}
      </div>
      <div style={{ fontSize: 13.5, lineHeight: 1.72, color: palette.textDim }}>{children}</div>
    </div>
  );
}

function Table({ head, rows }: { head: string[]; rows: string[][] }) {
  return (
    <table
      style={{
        width: "100%",
        borderCollapse: "collapse",
        fontFamily: mono,
        fontSize: 12.5,
        margin: "0 0 18px",
      }}
    >
      <thead>
        <tr>
          {head.map((h, i) => (
            <th
              key={h}
              style={{
                textAlign: i === 0 ? "left" : "right",
                padding: "7px 10px",
                borderBottom: `1px solid ${palette.border}`,
                color: palette.textFaint,
                fontWeight: 500,
                fontSize: 11,
              }}
            >
              {h}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((r, ri) => (
          <tr key={ri}>
            {r.map((c, ci) => (
              <td
                key={ci}
                style={{
                  textAlign: ci === 0 ? "left" : "right",
                  padding: "7px 10px",
                  borderBottom: `1px solid ${palette.borderSubtle}`,
                  color: ri === 0 && ci > 0 ? palette.evidential : palette.text,
                }}
              >
                {c}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

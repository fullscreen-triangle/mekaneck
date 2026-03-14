import React from "react";
import Head from "next/head";
import Link from "next/link";
import { motion } from "framer-motion";
import SectionLayout from "@/components/SectionLayout";
import RegimeBadge from "@/components/RegimeBadge";
import { InlineMath, BlockMath } from "@/components/Math";

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.6 },
  }),
};

const ResultRow = ({ label, value, note }) => (
  <div className="flex items-baseline justify-between py-2 border-b border-dark/5 dark:border-light/5 last:border-0">
    <span className="text-sm text-muted">{label}</span>
    <span className="text-sm font-mono text-dark dark:text-light">
      {value}
      {note && <span className="text-muted ml-2 text-xs">({note})</span>}
    </span>
  </div>
);

export default function Computing() {
  return (
    <>
      <Head>
        <title>Operator Trajectories | Neural Partition Language</title>
      </Head>

      {/* ── Hero ── */}
      <section className="relative min-h-[70vh] flex items-center overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern dark:bg-grid-pattern-dark bg-grid opacity-50" />
        <div className="relative z-10 w-full px-32 xl:px-24 lg:px-16 md:px-12 sm:px-8 py-24">
          <div className="max-w-4xl">
            <motion.div
              className="flex gap-2 mb-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              <RegimeBadge regime="coherent" />
              <RegimeBadge regime="locked" />
            </motion.div>
            <motion.p
              className="text-sm font-semibold text-primary dark:text-primaryDark uppercase tracking-widest mb-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              Paper III
            </motion.p>
            <motion.h1
              className="text-5xl font-bold text-dark dark:text-light leading-tight mb-6 xl:text-4xl md:text-3xl sm:text-2xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              Operator Trajectories in{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
                Neural Partition Space
              </span>
            </motion.h1>
            <motion.p
              className="text-lg text-muted max-w-2xl mb-8 md:text-base"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              A Formal Language for Bounded Phase-Space Computing
            </motion.p>
          </div>
        </div>
      </section>

      {/* ── 1. Partition Coordinates ── */}
      <SectionLayout id="partition-coordinates">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Partition Coordinates</h2>
          <p className="section-subheading">
            Neural states are indexed by quantum-like labels{" "}
            <InlineMath math="(n, \ell, m, s)" /> that discretize the bounded
            phase space into a countable partition lattice.
          </p>

          <div className="grid grid-cols-2 gap-6 mt-8 md:grid-cols-1">
            <motion.div className="card" variants={fadeUp} custom={0} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">Capacity Formula</h3>
              <BlockMath math="C(n) = 2n^2" />
              <p className="text-sm text-muted mt-3">
                The partition capacity at level <InlineMath math="n" /> exactly
                mirrors atomic electron-shell capacity. Validated for{" "}
                <InlineMath math="n = 1\text{--}7" />, giving capacities 2, 8,
                18, 32, 50, 72, 98 &mdash; exact match at every level.
              </p>
            </motion.div>

            <motion.div className="card" variants={fadeUp} custom={1} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">Depth Formula</h3>
              <BlockMath math="M(K, k) = K \cdot \log_3(k)" />
              <p className="text-sm text-muted mt-3">
                The computation depth grows logarithmically in the partition
                index <InlineMath math="k" />, scaled by the coupling
                strength <InlineMath math="K" />. This makes partition computing
                inherently efficient &mdash; exponential state spaces traversed
                in logarithmic time.
              </p>
            </motion.div>
          </div>

          <motion.div className="card mt-6" variants={fadeUp} custom={2} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h3 className="font-semibold text-dark dark:text-light mb-3">
              State Density in the <InlineMath math="(\ell, m)" /> Plane
            </h3>
            <p className="text-sm text-muted mb-4">
              Angular momentum selection rules constrain the accessible states.
              At each level <InlineMath math="\ell" />, the magnetic quantum
              number satisfies{" "}
              <InlineMath math="|m| \leq \ell" />, producing a triangular
              density in the <InlineMath math="(\ell, m)" /> plane. The spin
              degeneracy <InlineMath math="s = \pm\tfrac{1}{2}" /> doubles each
              state, recovering <InlineMath math="C(n) = 2n^2" />.
            </p>
            <BlockMath math="C(n) = \sum_{\ell=0}^{n-1} (2\ell + 1) \cdot 2 = 2n^2" />
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 2. S-Entropy Coordinate Space ── */}
      <SectionLayout id="s-entropy" className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">S-Entropy Coordinate Space</h2>
          <p className="section-subheading">
            Every neural state maps to a point in the S-entropy cube{" "}
            <InlineMath math="(S_k, S_t, S_e) \in [0,1]^3" />, a metric space
            with Euclidean geometry.
          </p>

          <div className="grid grid-cols-3 gap-6 mt-8 md:grid-cols-1">
            {[
              { coord: "S_k", name: "Kolmogorov", desc: "Algorithmic complexity of the neural trajectory" },
              { coord: "S_t", name: "Thermodynamic", desc: "Boltzmann entropy of the state distribution" },
              { coord: "S_e", name: "Entanglement", desc: "Quantum-like correlation between partition elements" },
            ].map((item, i) => (
              <motion.div key={item.coord} className="card text-center" variants={fadeUp} custom={i} initial="hidden" whileInView="visible" viewport={{ once: true }}>
                <div className="text-2xl font-bold text-primary dark:text-primaryDark mb-2">
                  <InlineMath math={item.coord} />
                </div>
                <h3 className="font-semibold text-dark dark:text-light text-sm mb-1">{item.name}</h3>
                <p className="text-xs text-muted">{item.desc}</p>
              </motion.div>
            ))}
          </div>

          <motion.div className="card mt-8" variants={fadeUp} custom={3} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h3 className="font-semibold text-dark dark:text-light mb-3">Metric Validation</h3>
            <BlockMath math="d(x, y) = \sqrt{(S_k^x - S_k^y)^2 + (S_t^x - S_t^y)^2 + (S_e^x - S_e^y)^2}" />
            <div className="grid grid-cols-2 gap-6 mt-4 md:grid-cols-1">
              <div>
                <ResultRow label="Triangle inequality violations" value="0" note="out of 1000 triples" />
                <ResultRow label="Maximum possible distance" value={<InlineMath math="\\sqrt{3} \\approx 1.732" />} />
                <ResultRow label="Observed maximum" value="1.348" />
              </div>
              <div className="text-sm text-muted">
                <p>
                  The S-entropy cube is a proper metric space under the
                  Euclidean norm. Zero triangle-inequality violations across
                  1000 randomly sampled point triples confirm metricity.
                  The gap between theoretical and observed maximum distance
                  reflects the physical constraint that extreme corners of the
                  cube are dynamically inaccessible.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 3. Trajectory-Terminus-Memory Triples ── */}
      <SectionLayout id="ttm-triples">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Trajectory-Terminus-Memory Triples</h2>
          <p className="section-subheading">
            Computation in partition space is captured by the triple{" "}
            <InlineMath math="\mathcal{M} = (\gamma,\, \Gamma_f,\, M)" />{" "}
            &mdash; a trajectory, its terminus, and the accumulated memory.
          </p>

          <motion.div className="card mt-8" variants={fadeUp} custom={0} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h3 className="font-semibold text-dark dark:text-light mb-4">Backward Determination (Poincar&eacute; Computing)</h3>
            <p className="text-sm text-muted mb-4">
              Unlike forward simulation, partition computing specifies the
              completion state <InlineMath math="\Gamma_f" /> first and derives
              the trajectory <InlineMath math="\gamma" /> backward. This is
              Poincar&eacute; computing: the terminus determines the path, not
              the other way around.
            </p>
            <BlockMath math="\gamma : [0, T] \to \mathcal{M}, \quad \gamma(T) = \Gamma_f" />
          </motion.div>

          <motion.div className="card mt-6" variants={fadeUp} custom={1} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h3 className="font-semibold text-dark dark:text-light mb-4">Memory as Arc Length</h3>
            <p className="text-sm text-muted mb-4">
              The accumulated memory along a trajectory is its arc length in
              S-entropy space. Different paths may reach the same terminus with
              different memories, encoding the computational history.
            </p>
            <BlockMath math="M(t) = \int_0^t \|\dot{\gamma}(\tau)\| \, d\tau" />
            <p className="text-sm text-muted mt-4">
              Multiple trajectories can converge to the same terminus{" "}
              <InlineMath math="\Gamma_f" /> but carry different memory values{" "}
              <InlineMath math="M" />. This distinguishes partition computing
              from simple attractor dynamics: the system remembers{" "}
              <em>how</em> it arrived, not just <em>where</em>.
            </p>
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 4. Operator Algebra ── */}
      <SectionLayout id="operator-algebra" className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Operator Algebra</h2>
          <p className="section-subheading">
            Neural interventions compose as operators on partition space.
            The fundamental composition is{" "}
            <InlineMath math="\texttt{APERTURE} \circ \texttt{REGIME} \circ \texttt{COUPLE}" />.
          </p>

          <motion.div className="card mt-8" variants={fadeUp} custom={0} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h3 className="font-semibold text-dark dark:text-light mb-4">Drug as Operator</h3>
            <p className="text-sm text-muted mb-4">
              A drug acts as an operator on neural partition space, transforming
              the system from one regime to another. The operator composition
              captures the full pharmacological effect.
            </p>
            <div className="flex items-center gap-4 justify-center my-6 flex-wrap">
              <div className="text-center">
                <p className="text-xs text-muted mb-1">Pre-drug</p>
                <RegimeBadge regime="turbulent" />
                <p className="text-xs font-mono text-muted mt-1">R = 0.135</p>
              </div>
              <div className="text-2xl text-primary dark:text-primaryDark">&rarr;</div>
              <div className="text-center px-4 py-2 border border-primary/20 rounded-lg">
                <p className="text-xs font-mono text-primary dark:text-primaryDark">
                  APERTURE &compfn; REGIME &compfn; COUPLE
                </p>
              </div>
              <div className="text-2xl text-primary dark:text-primaryDark">&rarr;</div>
              <div className="text-center">
                <p className="text-xs text-muted mb-1">Post-drug</p>
                <RegimeBadge regime="locked" />
                <p className="text-xs font-mono text-muted mt-1">R = 0.999</p>
              </div>
            </div>
          </motion.div>

          <motion.div className="card mt-6" variants={fadeUp} custom={1} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h3 className="font-semibold text-dark dark:text-light mb-4">Regime Distribution</h3>
            <p className="text-sm text-muted mb-4">
              Across 1001 sampled points in partition space, the five regimes
              occur with characteristic frequencies:
            </p>
            <div className="space-y-3">
              {[
                { regime: "turbulent", count: 301, pct: 30.1 },
                { regime: "aperture", count: 200, pct: 20.0 },
                { regime: "cascade", count: 299, pct: 29.9 },
                { regime: "coherent", count: 150, pct: 15.0 },
                { regime: "locked", count: 51, pct: 5.1 },
              ].map((item) => (
                <div key={item.regime} className="flex items-center gap-3">
                  <RegimeBadge regime={item.regime} />
                  <div className="flex-1 h-2 bg-dark/5 dark:bg-light/5 rounded-full overflow-hidden">
                    <motion.div
                      className={`h-full rounded-full bg-regime-${item.regime}`}
                      initial={{ width: 0 }}
                      whileInView={{ width: `${item.pct}%` }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.8 }}
                    />
                  </div>
                  <span className="text-xs font-mono text-muted w-16 text-right">
                    {item.count}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 5. pNPL Type System ── */}
      <SectionLayout id="pnpl-types">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">pNPL Type System</h2>
          <p className="section-subheading">
            The partition Neural Partition Language (pNPL) formalizes neural
            computation with a type-safe grammar. Every object has a type;
            every composition is checked.
          </p>

          <div className="grid grid-cols-2 gap-6 mt-8 md:grid-cols-1">
            {[
              { type: "State", sig: "\\texttt{State} : (n, \\ell, m, s) \\to \\Omega", desc: "A point in partition space, indexed by quantum numbers" },
              { type: "Operator", sig: "\\texttt{Operator} : \\texttt{State} \\to \\texttt{State}", desc: "A morphism between states, e.g. a drug or stimulus" },
              { type: "Trajectory", sig: "\\texttt{Trajectory} : [0,T] \\to \\texttt{State}", desc: "A continuous path through partition space" },
              { type: "Regime", sig: "\\texttt{Regime} : \\texttt{State} \\to \\{1,...,5\\}", desc: "Classification by Kuramoto order parameter R" },
            ].map((item, i) => (
              <motion.div key={item.type} className="card" variants={fadeUp} custom={i} initial="hidden" whileInView="visible" viewport={{ once: true }}>
                <h3 className="font-semibold text-dark dark:text-light mb-2">{item.type}</h3>
                <div className="bg-dark/[0.03] dark:bg-light/[0.03] rounded-lg p-3 mb-3">
                  <InlineMath math={item.sig} />
                </div>
                <p className="text-sm text-muted">{item.desc}</p>
              </motion.div>
            ))}
          </div>

          <motion.div className="card mt-6" variants={fadeUp} custom={4} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h3 className="font-semibold text-dark dark:text-light mb-3">Type-Safe Composition</h3>
            <p className="text-sm text-muted mb-4">
              Operator composition is type-checked: the codomain of the inner
              operator must match the domain of the outer. Partition coordinates
              serve as quantum numbers that index the type hierarchy.
            </p>
            <BlockMath math="(\texttt{Op}_2 \circ \texttt{Op}_1) : \texttt{State} \to \texttt{State} \quad \text{iff} \quad \text{codomain}(\texttt{Op}_1) \subseteq \text{domain}(\texttt{Op}_2)" />
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 6. Synchronization Onset ── */}
      <SectionLayout id="sync-onset" className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Synchronization Onset</h2>
          <p className="section-subheading">
            The critical coupling <InlineMath math="K_c" /> determines the
            onset of synchronization. Validated across 5 frequency conditions.
          </p>

          <motion.div className="card mt-8" variants={fadeUp} custom={0} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <BlockMath math="K_c = \frac{2}{\pi g(0)}" />
            <p className="text-sm text-muted mt-4 mb-4">
              The critical coupling threshold is set by the natural frequency
              distribution <InlineMath math="g(\omega)" /> evaluated at zero
              detuning. Five independent frequency conditions &mdash; from
              narrow unimodal to broad bimodal &mdash; each yield a{" "}
              <InlineMath math="K_c" /> that correctly predicts the transition
              from turbulent to cascade regime.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-dark/10 dark:border-light/10">
                    <th className="text-left py-2 text-muted font-medium">Condition</th>
                    <th className="text-right py-2 text-muted font-medium">Predicted <InlineMath math="K_c" /></th>
                    <th className="text-right py-2 text-muted font-medium">Observed</th>
                    <th className="text-right py-2 text-muted font-medium">Match</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { cond: "Narrow unimodal", pred: "1.27", obs: "1.25", match: true },
                    { cond: "Broad unimodal", pred: "2.54", obs: "2.51", match: true },
                    { cond: "Bimodal symmetric", pred: "3.18", obs: "3.15", match: true },
                    { cond: "Bimodal asymmetric", pred: "3.82", obs: "3.79", match: true },
                    { cond: "Uniform", pred: "6.37", obs: "6.33", match: true },
                  ].map((row) => (
                    <tr key={row.cond} className="border-b border-dark/5 dark:border-light/5">
                      <td className="py-2 text-dark dark:text-light">{row.cond}</td>
                      <td className="py-2 text-right font-mono">{row.pred}</td>
                      <td className="py-2 text-right font-mono">{row.obs}</td>
                      <td className="py-2 text-right">{row.match ? "Yes" : "No"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 7. Frequency Hierarchy ── */}
      <SectionLayout id="frequency-hierarchy">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Frequency Hierarchy</h2>
          <p className="section-subheading">
            A gear cascade spans 18 orders of magnitude, from molecular vibrations
            at <InlineMath math="10^{13}" /> Hz to behavioral output at 1 Hz.
          </p>

          <motion.div className="card mt-8" variants={fadeUp} custom={0} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h3 className="font-semibold text-dark dark:text-light mb-4">Partition Gear Mechanism</h3>
            <p className="text-sm text-muted mb-6">
              Each partition level acts as a frequency divider. The gear ratio
              between adjacent levels is determined by the partition capacity{" "}
              <InlineMath math="C(n) = 2n^2" />, producing an exponential
              slowing across the hierarchy. This adiabatic separation justifies
              the Born-Oppenheimer factorization used throughout the framework.
            </p>

            <div className="space-y-2">
              {[
                { level: "Molecular vibrations", freq: "10^{13}", hz: "10 THz" },
                { level: "Protein conformational", freq: "10^{9}", hz: "1 GHz" },
                { level: "Ion channel gating", freq: "10^{6}", hz: "1 MHz" },
                { level: "Synaptic transmission", freq: "10^{3}", hz: "1 kHz" },
                { level: "Neural oscillation", freq: "10^{1}", hz: "10 Hz" },
                { level: "Cognitive rhythm", freq: "10^{0}", hz: "1 Hz" },
                { level: "Behavioral output", freq: "10^{-1}", hz: "0.1 Hz" },
              ].map((item, i) => (
                <motion.div
                  key={item.level}
                  className="flex items-center gap-4 py-2 px-4 rounded-lg bg-dark/[0.02] dark:bg-light/[0.02]"
                  variants={fadeUp}
                  custom={i * 0.5}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                >
                  <span className="text-xs font-mono text-primary dark:text-primaryDark w-16">
                    {item.hz}
                  </span>
                  <div className="flex-1 text-sm text-dark dark:text-light">{item.level}</div>
                  <InlineMath math={item.freq} />
                </motion.div>
              ))}
            </div>
          </motion.div>

          <motion.div className="card mt-6" variants={fadeUp} custom={1} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h3 className="font-semibold text-dark dark:text-light mb-3">Consciousness as Decay Curve Intersection</h3>
            <p className="text-sm text-muted">
              Consciousness emerges at the intersection of two decay curves:
              the top-down attentional cascade (decaying from behavioral
              frequencies downward) and the bottom-up thermodynamic cascade
              (decaying from molecular frequencies upward). The intersection
              at <InlineMath math="\sim 10" /> Hz corresponds to the alpha
              rhythm, the signature frequency of conscious awareness. This
              is not postulated but derived from the gear cascade and the
              partition capacity formula.
            </p>
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 8. Figure Placeholders ── */}
      <SectionLayout id="figures" className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-5xl mx-auto">
          <h2 className="section-heading text-center">Figures</h2>
          <div className="grid grid-cols-3 gap-6 mt-8 md:grid-cols-2 sm:grid-cols-1">
            {[
              { num: 1, title: "Partition Lattice", desc: "Capacity C(n) = 2n\u00B2 validated for n = 1\u20137" },
              { num: 2, title: "S-Entropy Cube", desc: "1000-point metric validation with zero triangle-inequality violations" },
              { num: 3, title: "Trajectory Bundles", desc: "Multiple paths converging to common terminus with distinct memories" },
              { num: 4, title: "Operator Composition", desc: "APERTURE \u2218 REGIME \u2218 COUPLE pipeline on drug data" },
              { num: 5, title: "Synchronization Onset", desc: "K_c validation across 5 frequency conditions" },
              { num: 6, title: "Frequency Gear Cascade", desc: "18 orders of magnitude from molecular to behavioral" },
            ].map((fig, i) => (
              <motion.div
                key={fig.num}
                className="card !p-0 overflow-hidden"
                variants={fadeUp}
                custom={i}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
              >
                <div className="h-40 bg-gradient-to-br from-primary/5 to-accent/5 flex items-center justify-center">
                  <span className="text-4xl font-bold text-primary/20 dark:text-primaryDark/20">
                    Fig. {fig.num}
                  </span>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-dark dark:text-light text-sm mb-1">{fig.title}</h3>
                  <p className="text-xs text-muted">{fig.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </SectionLayout>

      {/* ── 9. Key Results ── */}
      <SectionLayout id="key-results">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading text-center">Key Results</h2>
          <div className="grid grid-cols-2 gap-6 mt-8 md:grid-cols-1">
            {[
              { stat: "10/10", label: "NPL claims validated" },
              { stat: "Exact", label: "C(n) = 2n\u00B2 match for n = 1\u20137" },
              { stat: "0", label: "Triangle inequality violations" },
              { stat: "Valid", label: "Operator composition across regimes" },
            ].map((item, i) => (
              <motion.div
                key={item.label}
                className="card text-center"
                variants={fadeUp}
                custom={i}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
              >
                <div className="text-3xl font-bold text-primary dark:text-primaryDark mb-2">
                  {item.stat}
                </div>
                <p className="text-sm text-muted">{item.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </SectionLayout>

      {/* ── Navigation ── */}
      <SectionLayout className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-between items-center md:flex-col md:gap-6">
            <Link href="/apertures" className="group flex items-center gap-3 text-dark dark:text-light hover:text-primary dark:hover:text-primaryDark transition-colors">
              <span className="text-2xl">&larr;</span>
              <div>
                <p className="text-xs text-muted">Previous</p>
                <p className="font-semibold group-hover:text-primary dark:group-hover:text-primaryDark transition-colors">Geometric Apertures</p>
              </div>
            </Link>
            <Link href="/lagrangian" className="group flex items-center gap-3 text-right text-dark dark:text-light hover:text-primary dark:hover:text-primaryDark transition-colors">
              <div>
                <p className="text-xs text-muted">Next</p>
                <p className="font-semibold group-hover:text-primary dark:group-hover:text-primaryDark transition-colors">The Neural Partition Lagrangian</p>
              </div>
              <span className="text-2xl">&rarr;</span>
            </Link>
          </div>
        </div>
      </SectionLayout>
    </>
  );
}

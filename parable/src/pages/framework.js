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

const AxiomCard = ({ number, title, description, math, color, delay }) => (
  <motion.div
    className="card"
    variants={fadeUp}
    custom={delay}
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true }}
  >
    <div
      className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center text-white font-bold text-lg mb-5`}
    >
      {number}
    </div>
    <h3 className="text-xl font-semibold text-dark dark:text-light mb-2">
      {title}
    </h3>
    <p className="text-sm text-muted mb-4">{description}</p>
    <div className="bg-dark/[0.03] dark:bg-light/[0.03] rounded-lg p-3">
      <BlockMath math={math} />
    </div>
  </motion.div>
);

const RegimeRow = ({ regime, name, range, R, meaning, examples, delay }) => (
  <motion.div
    className="card !p-5 flex items-start gap-4 md:flex-col"
    variants={fadeUp}
    custom={delay}
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true }}
  >
    <div className="flex-shrink-0 w-28 md:w-full">
      <RegimeBadge regime={regime} />
      <div className="text-xs font-mono text-muted mt-2">{range}</div>
    </div>
    <div className="flex-1">
      <h4 className="font-semibold text-dark dark:text-light mb-1">{name}</h4>
      <p className="text-sm text-muted mb-2">{meaning}</p>
      <p className="text-xs text-muted/70 italic">{examples}</p>
    </div>
  </motion.div>
);

const NavCard = ({ title, subtitle, href, delay }) => (
  <motion.div
    variants={fadeUp}
    custom={delay}
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true }}
  >
    <Link href={href} className="block card group cursor-pointer">
      <h3 className="text-lg font-semibold text-dark dark:text-light mb-2 group-hover:text-primary dark:group-hover:text-primaryDark transition-colors">
        {title}
      </h3>
      <p className="text-sm text-muted">{subtitle}</p>
      <div className="mt-3 text-primary dark:text-primaryDark text-sm font-medium">
        Read more &rarr;
      </div>
    </Link>
  </motion.div>
);

export default function Framework() {
  return (
    <>
      <Head>
        <title>The Partition Framework | Neural Partition Language</title>
        <meta
          name="description"
          content="Three thermodynamic axioms, one Lagrangian, five operational regimes. The complete mathematical framework for neural dynamics derived from first principles."
        />
      </Head>

      {/* Hero */}
      <section className="relative min-h-[70vh] flex items-center overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern dark:bg-grid-pattern-dark bg-grid opacity-50" />
        <div className="relative z-10 w-full px-32 xl:px-24 lg:px-16 md:px-12 sm:px-8 py-16">
          <div className="max-w-4xl mx-auto text-center">
            <motion.p
              className="text-sm font-semibold text-primary dark:text-primaryDark uppercase tracking-widest mb-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              First Principles
            </motion.p>
            <motion.h1
              className="text-5xl font-bold text-dark dark:text-light leading-tight mb-6 xl:text-4xl md:text-3xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              The{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
                Partition Framework
              </span>
            </motion.h1>
            <motion.p
              className="text-lg text-muted max-w-2xl mx-auto mb-8 md:text-base"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              Three axioms constrain neural phase space. From these constraints alone,
              the entire architecture of brain dynamics &mdash; five regimes, partition
              coordinates, entropy geometry, and conservation laws &mdash; follows as
              mathematical necessity.
            </motion.p>
            <motion.div
              className="inline-block bg-dark/[0.03] dark:bg-light/[0.03] rounded-xl px-8 py-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <BlockMath math="\mathcal{L}[\mathbf{q}, \dot{\mathbf{q}}] = T(\dot{\mathbf{q}}) - V(\mathbf{q}) + \lambda \cdot g(\mathbf{q})" />
            </motion.div>
          </div>
        </div>
      </section>

      {/* Three Axioms */}
      <SectionLayout id="axioms">
        <div className="max-w-5xl mx-auto">
          <h2 className="section-heading text-center">Three Axioms</h2>
          <p className="section-subheading text-center mx-auto">
            The entire framework rests on three physically motivated constraints.
            No free parameters, no curve-fitting &mdash; just thermodynamic necessity.
          </p>
          <div className="grid grid-cols-3 gap-6 mt-12 md:grid-cols-1">
            <AxiomCard
              number="I"
              title="Bounded Phase Space"
              description="The neural state space has finite measure. Biological systems operate within bounded energy, bounded firing rates, and bounded connectivity. This rules out infinite-dimensional pathologies."
              math="\mu(\Omega) < \infty"
              color="from-regime-turbulent to-regime-aperture"
              delay={0}
            />
            <AxiomCard
              number="II"
              title="No Null State"
              description="The system is never completely inactive. Even in deep sleep or anaesthesia, neural activity persists. There is no zero vector in the allowable state space."
              math="\forall\, t: \quad \mathbf{q}(t) \neq \mathbf{0}"
              color="from-regime-cascade to-regime-coherent"
              delay={1}
            />
            <AxiomCard
              number="III"
              title="Finite Resolution"
              description="Every measurement has a minimum granularity. We cannot resolve neural states below a fundamental precision threshold, set by the physics of observation."
              math="\exists\; \delta > 0 : \quad \|q_i - q_j\| < \delta \implies q_i \sim q_j"
              color="from-regime-coherent to-regime-locked"
              delay={2}
            />
          </div>
          <motion.p
            className="text-sm text-muted text-center mt-8 max-w-2xl mx-auto"
            variants={fadeUp}
            custom={3}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            Together, these axioms force the state space into a compact manifold with
            a natural partition structure. Every consequence that follows &mdash;
            regime classification, entropy geometry, conservation laws &mdash; is a
            theorem, not an assumption.
          </motion.p>
        </div>
      </SectionLayout>

      {/* Partition Coordinates */}
      <SectionLayout
        id="coordinates"
        className="bg-dark/[0.02] dark:bg-light/[0.02]"
      >
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading text-center">Partition Coordinates</h2>
          <p className="section-subheading text-center mx-auto">
            Axiom III forces the state space into discrete cells, indexed by four
            quantum numbers analogous to atomic orbitals.
          </p>

          <motion.div
            className="bg-dark/[0.03] dark:bg-light/[0.03] rounded-xl p-6 my-8 text-center"
            variants={fadeUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <BlockMath math="|n, \ell, m, s\rangle \quad \text{with capacity} \quad C(n) = 2n^2" />
          </motion.div>

          <div className="grid grid-cols-2 gap-6 md:grid-cols-1">
            {[
              {
                symbol: "n",
                name: "Principal Number",
                desc: "Determines the shell level and total capacity. Higher n means more available states within that partition.",
              },
              {
                symbol: "\u2113",
                name: "Angular Number",
                desc: "Encodes the mode shape within a shell. Ranges from 0 to n-1, analogous to orbital angular momentum.",
              },
              {
                symbol: "m",
                name: "Magnetic Number",
                desc: "Specifies orientation within a subshell. Ranges from -\u2113 to +\u2113, breaking directional degeneracy.",
              },
              {
                symbol: "s",
                name: "Spin Number",
                desc: "Binary label for complementary state pairs within each cell. Takes values +1/2 or -1/2.",
              },
            ].map((item, i) => (
              <motion.div
                key={item.symbol}
                className="card !p-5"
                variants={fadeUp}
                custom={i}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="w-10 h-10 rounded-lg bg-primary/10 text-primary dark:text-primaryDark flex items-center justify-center font-bold text-lg font-mono">
                    {item.symbol}
                  </span>
                  <h4 className="font-semibold text-dark dark:text-light">
                    {item.name}
                  </h4>
                </div>
                <p className="text-sm text-muted">{item.desc}</p>
              </motion.div>
            ))}
          </div>

          <motion.p
            className="text-sm text-muted text-center mt-8 max-w-2xl mx-auto"
            variants={fadeUp}
            custom={4}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            The capacity formula <InlineMath math="C(n) = 2n^2" /> mirrors the
            degeneracy of hydrogen-like atoms. This is not analogy &mdash; it is a
            structural consequence of the same symmetry group acting on a bounded
            domain.
          </motion.p>
        </div>
      </SectionLayout>

      {/* S-Entropy Space */}
      <SectionLayout id="entropy">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading text-center">S-Entropy Space</h2>
          <p className="section-subheading text-center mx-auto">
            Every neural state maps to a point in a three-dimensional entropy cube,
            defining a natural metric for distance between brain states.
          </p>

          <motion.div
            className="bg-dark/[0.03] dark:bg-light/[0.03] rounded-xl p-6 my-8 text-center"
            variants={fadeUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <BlockMath math="(S_k,\; S_t,\; S_e) \;\in\; [0,1]^3" />
          </motion.div>

          <div className="grid grid-cols-3 gap-6 md:grid-cols-1">
            {[
              {
                label: "S_k",
                name: "Kolmogorov Entropy",
                desc: "Measures dynamical complexity &mdash; the rate of information production. High S_k indicates chaotic, information-rich dynamics.",
                color: "text-regime-turbulent",
              },
              {
                label: "S_t",
                name: "Topological Entropy",
                desc: "Counts the number of distinguishable orbits. High S_t means the system explores many structurally distinct trajectories.",
                color: "text-regime-cascade",
              },
              {
                label: "S_e",
                name: "Entanglement Entropy",
                desc: "Quantifies inter-partition correlations. High S_e signals strong coupling between subsystems, characteristic of coherent states.",
                color: "text-regime-coherent",
              },
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
                <div
                  className={`text-3xl font-bold font-mono ${item.color} mb-2`}
                >
                  <InlineMath math={item.label} />
                </div>
                <h4 className="font-semibold text-dark dark:text-light mb-2">
                  {item.name}
                </h4>
                <p
                  className="text-sm text-muted"
                  dangerouslySetInnerHTML={{ __html: item.desc }}
                />
              </motion.div>
            ))}
          </div>

          <motion.div
            className="mt-8 text-center"
            variants={fadeUp}
            custom={3}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <p className="text-sm text-muted max-w-2xl mx-auto">
              The metric on S-entropy space,{" "}
              <InlineMath math="d(\mathbf{S}_1, \mathbf{S}_2) = \|\mathbf{S}_1 - \mathbf{S}_2\|_2" />
              , gives a principled distance between neural states. Two brain states
              are &ldquo;close&rdquo; precisely when they share similar complexity,
              topology, and correlation structure.
            </p>
          </motion.div>
        </div>
      </SectionLayout>

      {/* Five Regimes */}
      <SectionLayout
        id="regimes"
        className="bg-dark/[0.02] dark:bg-light/[0.02]"
      >
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading text-center">Five Operational Regimes</h2>
          <p className="section-subheading text-center mx-auto">
            The Kuramoto order parameter <InlineMath math="R \in [0, 1]" /> partitions
            the full state space into five regimes with sharp boundaries.
            Every neural state belongs to exactly one regime.
          </p>

          <div className="flex flex-col gap-4 mt-12">
            <RegimeRow
              regime="turbulent"
              name="Turbulent"
              range="R < 0.3"
              R="Low"
              meaning="Complete desynchronization. Oscillators fire independently with no phase coherence. Associated with pathological states where organized neural communication breaks down."
              examples="e.g. Severe anaesthesia, cortical spreading depression, some seizure onset patterns"
              delay={0}
            />
            <RegimeRow
              regime="aperture"
              name="Aperture"
              range="0.3 &le; R < 0.5"
              R="Sub-critical"
              meaning="Selective gating emerges. The system begins to filter inputs, allowing some signals through while blocking others. This is the regime of pharmacological action and receptor selectivity."
              examples="e.g. SSRI action, enzyme substrate selection, early sleep onset (N1)"
              delay={1}
            />
            <RegimeRow
              regime="cascade"
              name="Cascade"
              range="0.5 &le; R < 0.8"
              R="Critical"
              meaning="Cooperative synchronization. Oscillators self-organize into partially coherent clusters. Information processing is maximally flexible, balancing stability and adaptability."
              examples="e.g. Working memory, attentional focus, REM sleep, creative problem-solving"
              delay={2}
            />
            <RegimeRow
              regime="coherent"
              name="Coherent"
              range="0.8 &le; R < 0.95"
              R="High"
              meaning="Stable, globally synchronized operation. The healthy resting baseline of the awake brain. Strong inter-regional coupling supports efficient communication."
              examples="e.g. Relaxed wakefulness, deep NREM sleep (N3), meditation, flow states"
              delay={3}
            />
            <RegimeRow
              regime="locked"
              name="Phase-Locked"
              range="R &ge; 0.95"
              R="Maximal"
              meaning="Hypersynchrony. All oscillators lock into rigid phase alignment, destroying information-processing capacity. The system becomes maximally ordered but computationally frozen."
              examples="e.g. Tonic-clonic seizure, status epilepticus, certain drug overdoses"
              delay={4}
            />
          </div>
        </div>
      </SectionLayout>

      {/* Kuramoto Synchronization */}
      <SectionLayout id="kuramoto">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading text-center">
            Kuramoto Synchronization
          </h2>
          <p className="section-subheading text-center mx-auto">
            The order parameter <InlineMath math="R" /> emerges from the
            Kuramoto model of coupled oscillators, providing the
            measurable quantity that classifies every neural state.
          </p>

          <motion.div
            className="bg-dark/[0.03] dark:bg-light/[0.03] rounded-xl p-6 my-8 text-center"
            variants={fadeUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <BlockMath math="R\, e^{i\psi} = \frac{1}{N} \sum_{j=1}^{N} e^{i\theta_j}" />
          </motion.div>

          <div className="grid grid-cols-2 gap-6 md:grid-cols-1">
            <motion.div
              className="card"
              variants={fadeUp}
              custom={0}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              <h4 className="font-semibold text-dark dark:text-light mb-3">
                Order Parameter
              </h4>
              <p className="text-sm text-muted mb-3">
                The magnitude <InlineMath math="R" /> measures the degree of phase
                coherence across <InlineMath math="N" /> neural oscillators.
                When <InlineMath math="R \to 0" />, phases are uniformly distributed
                (incoherence). When <InlineMath math="R \to 1" />, all oscillators
                are phase-locked (hypersynchrony).
              </p>
              <p className="text-sm text-muted">
                The mean phase <InlineMath math="\psi" /> gives the collective
                rhythm&apos;s instantaneous phase, observable in EEG/MEG recordings.
              </p>
            </motion.div>
            <motion.div
              className="card"
              variants={fadeUp}
              custom={1}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              <h4 className="font-semibold text-dark dark:text-light mb-3">
                Critical Coupling
              </h4>
              <p className="text-sm text-muted mb-4">
                Synchronization undergoes a phase transition at the critical coupling
                strength <InlineMath math="K_c" />, determined by the natural frequency
                distribution width <InlineMath math="\sigma_\omega" />:
              </p>
              <div className="bg-dark/[0.03] dark:bg-light/[0.03] rounded-lg p-3">
                <BlockMath math="K_c = \frac{2\,\sigma_\omega}{\pi}" />
              </div>
              <p className="text-sm text-muted mt-3">
                Below <InlineMath math="K_c" />, the system remains incoherent.
                Above it, a macroscopic fraction of oscillators spontaneously
                synchronize &mdash; the onset of neural coherence.
              </p>
            </motion.div>
          </div>
        </div>
      </SectionLayout>

      {/* Structural Factor */}
      <SectionLayout
        id="structural-factor"
        className="bg-dark/[0.02] dark:bg-light/[0.02]"
      >
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading text-center">The Structural Factor</h2>
          <p className="section-subheading text-center mx-auto">
            Coherence alone does not determine neural function.
            The structural factor couples the order parameter with
            phase variance to yield a single quality metric for brain states.
          </p>

          <motion.div
            className="bg-dark/[0.03] dark:bg-light/[0.03] rounded-xl p-6 my-8 text-center"
            variants={fadeUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <BlockMath math="S(R,\, \sigma^2) = R \cdot \exp\!\left(-\frac{\sigma^2}{2\pi^2}\right)" />
          </motion.div>

          <div className="grid grid-cols-2 gap-6 md:grid-cols-1">
            <motion.div
              className="card"
              variants={fadeUp}
              custom={0}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              <h4 className="font-semibold text-dark dark:text-light mb-2">
                Why both R and &sigma;&sup2;?
              </h4>
              <p className="text-sm text-muted">
                A high <InlineMath math="R" /> with large phase variance indicates
                fragile synchrony &mdash; a state that appears coherent but is
                vulnerable to perturbation. The exponential damping penalizes
                variance, ensuring <InlineMath math="S" /> peaks only for
                robust coherence.
              </p>
            </motion.div>
            <motion.div
              className="card"
              variants={fadeUp}
              custom={1}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              <h4 className="font-semibold text-dark dark:text-light mb-2">
                Physical interpretation
              </h4>
              <p className="text-sm text-muted">
                <InlineMath math="S \to 1" />: maximal robust coherence (healthy
                wakefulness). <InlineMath math="S \to 0" />: either incoherent or
                noisy synchrony. The structural factor is directly measurable from
                EEG phase data and tracks consciousness level during anaesthesia.
              </p>
            </motion.div>
          </div>
        </div>
      </SectionLayout>

      {/* Triple Equivalence */}
      <SectionLayout id="triple-equivalence">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading text-center">Triple Equivalence</h2>
          <p className="section-subheading text-center mx-auto">
            The deepest result of the framework: three independently defined
            entropies &mdash; oscillatory, categorical, and partition &mdash;
            are provably equal. This is the partition analogue of the
            holographic principle.
          </p>

          <motion.div
            className="bg-gradient-to-br from-primary/5 to-accent/5 border border-primary/10 rounded-xl p-8 my-8 text-center"
            variants={fadeUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <BlockMath math="S_{\text{osc}} \;=\; S_{\text{cat}} \;=\; S_{\text{part}} \;=\; k_B\, M \ln n" />
          </motion.div>

          <div className="grid grid-cols-3 gap-6 md:grid-cols-1">
            {[
              {
                label: "S_{\\text{osc}}",
                name: "Oscillatory Entropy",
                desc: "Computed from the phase distribution of Kuramoto oscillators. Captures the dynamical degrees of freedom.",
              },
              {
                label: "S_{\\text{cat}}",
                name: "Categorical Entropy",
                desc: "Derived from the morphism count in the category of neural states. A purely algebraic quantity.",
              },
              {
                label: "S_{\\text{part}}",
                name: "Partition Entropy",
                desc: "Counted from the partition coordinates (n, l, m, s). A combinatorial quantity arising from Axiom III.",
              },
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
                <div className="text-xl font-bold text-primary dark:text-primaryDark mb-2">
                  <InlineMath math={item.label} />
                </div>
                <h4 className="font-semibold text-dark dark:text-light mb-2">
                  {item.name}
                </h4>
                <p className="text-sm text-muted">{item.desc}</p>
              </motion.div>
            ))}
          </div>

          <motion.p
            className="text-sm text-muted text-center mt-8 max-w-2xl mx-auto"
            variants={fadeUp}
            custom={3}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            The triple equivalence means you can compute the entropy of a neural
            state from whichever representation is most convenient &mdash; phase
            data, algebraic structure, or combinatorial partition &mdash; and arrive
            at the same answer. This is the hallmark of a fundamental theory.
          </motion.p>
        </div>
      </SectionLayout>

      {/* Navigation to Detail Pages */}
      <SectionLayout className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-5xl mx-auto">
          <h2 className="section-heading text-center">Explore Further</h2>
          <p className="section-subheading text-center mx-auto">
            Each pillar of the framework is developed in full detail with
            derivations, experimental validation, and interactive visualizations.
          </p>
          <div className="grid grid-cols-2 gap-6 mt-12 md:grid-cols-1">
            <NavCard
              title="Operational Regime Classification"
              subtitle="Kuramoto synchronization, five regimes, EEG validation across 500 sleep epochs, and the complete sleep-stage mapping."
              href="/regimes"
              delay={0}
            />
            <NavCard
              title="Geometric Apertures"
              subtitle="Zero-work selectivity, monopole/dipole/quadrupole taxonomy, 11 antidepressants modeled, 12 enzymes validated."
              href="/apertures"
              delay={1}
            />
            <NavCard
              title="Operator Trajectories &amp; Computing"
              subtitle="Partition coordinates as a computing substrate. Poincare computing, backward determination, and the pNPL type system."
              href="/computing"
              delay={2}
            />
            <NavCard
              title="The Neural Partition Lagrangian"
              subtitle="Onsager-Machlup action, Noether conservation laws, and the complete derivation of 28 validated predictions from one equation."
              href="/lagrangian"
              delay={3}
            />
          </div>
        </div>
      </SectionLayout>
    </>
  );
}

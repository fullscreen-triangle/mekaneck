import React from "react";
import Head from "next/head";
import Link from "next/link";
import { motion } from "framer-motion";
import SectionLayout from "@/components/SectionLayout";
import RegimeBadge from "@/components/RegimeBadge";
import Layout from "@/components/Layout";
import { InlineMath, BlockMath } from "@/components/Math";

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.6 },
  }),
};

const FigurePlaceholder = ({ panel, description }) => (
  <motion.div
    className="card flex flex-col items-center justify-center min-h-[220px] border-2 border-dashed border-dark/10 dark:border-light/10"
    variants={fadeUp}
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true }}
  >
    <div className="text-xs uppercase tracking-widest text-muted mb-2">
      Panel {panel}
    </div>
    <p className="text-sm text-muted text-center max-w-xs">{description}</p>
  </motion.div>
);

const ValidationBadge = ({ label, value }) => (
  <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 text-green-600 dark:text-green-400 text-xs font-semibold">
    <span className="w-2 h-2 rounded-full bg-green-500" />
    {label}: {value}
  </div>
);

export default function Regimes() {
  return (
    <>
      <Head>
        <title>Operational Regime Classification | Neural Partition Language</title>
      </Head>

      {/* Hero */}
      <section className="relative min-h-[60vh] flex items-center overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern dark:bg-grid-pattern-dark bg-grid opacity-50" />
        <div className="relative z-10 w-full px-32 xl:px-24 lg:px-16 md:px-12 sm:px-8 py-20">
          <div className="max-w-4xl mx-auto text-center">
            <motion.p
              className="text-sm font-semibold text-primary dark:text-primaryDark uppercase tracking-widest mb-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              Paper I
            </motion.p>
            <motion.h1
              className="text-5xl font-bold text-dark dark:text-light leading-tight mb-6 xl:text-4xl md:text-3xl sm:text-2xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              Operational Regime{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
                Classification
              </span>
            </motion.h1>
            <motion.p
              className="text-lg text-muted max-w-2xl mx-auto mb-8 md:text-base"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              From Thermodynamic Axioms to Sleep Architecture
            </motion.p>
            <motion.div
              className="flex gap-3 justify-center flex-wrap"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <ValidationBadge label="Sleep claims" value="6/6" />
              <ValidationBadge label="R ordering" value="preserved" />
              <ValidationBadge label="Variance slope" value="-1.0 exact" />
            </motion.div>
          </div>
        </div>
      </section>

      {/* Introduction */}
      <SectionLayout id="introduction">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Introduction</h2>
          <p className="section-subheading">
            How do we classify the operational state of a brain? Existing
            approaches rely on spectral power bands or heuristic staging rules.
            We show that three thermodynamic axioms&mdash;bounded phase space,
            no null state, and finite observational resolution&mdash;are
            sufficient to derive a complete classification of neural regimes.
          </p>
          <div className="grid grid-cols-3 gap-6 mt-8 md:grid-cols-1">
            {[
              {
                axiom: "I",
                title: "Bounded Phase Space",
                desc: "The neural state space has finite measure: \u03BC(\u03A9) < \u221E. No infinite-energy configurations are accessible.",
                color: "from-regime-turbulent to-regime-aperture",
              },
              {
                axiom: "II",
                title: "No Null State",
                desc: "The system is never in a state of zero activity. Even under deep anesthesia, residual oscillations persist.",
                color: "from-regime-cascade to-regime-coherent",
              },
              {
                axiom: "III",
                title: "Finite Resolution",
                desc: "Observational precision is bounded: \u03B4 > 0. This imposes a natural coarse-graining on the partition.",
                color: "from-regime-coherent to-regime-locked",
              },
            ].map((item, i) => (
              <motion.div
                key={item.axiom}
                className="card text-left"
                variants={fadeUp}
                custom={i}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
              >
                <div
                  className={`w-10 h-10 rounded-lg bg-gradient-to-br ${item.color} flex items-center justify-center text-white font-bold text-sm mb-4`}
                >
                  {item.axiom}
                </div>
                <h3 className="font-semibold text-dark dark:text-light mb-2">
                  {item.title}
                </h3>
                <p className="text-sm text-muted">{item.desc}</p>
              </motion.div>
            ))}
          </div>
          <p className="text-muted mt-8 leading-relaxed">
            These axioms uniquely determine the Kuramoto model as the
            appropriate mathematical backbone for regime classification. The
            order parameter{" "}
            <InlineMath math="R" /> serves as the single
            sufficient statistic that partitions neural dynamics into five
            operationally distinct regimes, each with characteristic
            synchronization profiles, spectral signatures, and functional
            correlates.
          </p>
        </div>
      </SectionLayout>

      {/* Kuramoto Model */}
      <SectionLayout
        id="kuramoto"
        className="bg-dark/[0.02] dark:bg-light/[0.02]"
      >
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">The Kuramoto Model</h2>
          <p className="section-subheading">
            A population of <InlineMath math="N" /> coupled oscillators with
            natural frequencies drawn from a distribution with spread{" "}
            <InlineMath math="\sigma_\omega" />.
          </p>

          <div className="space-y-8 mt-8">
            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-4">
                Mean-Field Dynamics
              </h3>
              <p className="text-sm text-muted mb-4">
                Each oscillator evolves according to the mean-field coupling:
              </p>
              <BlockMath math="\frac{d\theta_j}{dt} = \omega_j + \frac{K}{N} \sum_{k=1}^{N} \sin(\theta_k - \theta_j)" />
              <p className="text-sm text-muted mt-4">
                where <InlineMath math="\omega_j" /> is the natural frequency of
                oscillator <InlineMath math="j" /> and{" "}
                <InlineMath math="K" /> is the global coupling strength.
              </p>
            </div>

            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-4">
                Order Parameter
              </h3>
              <p className="text-sm text-muted mb-4">
                The degree of phase coherence is captured by the Kuramoto order
                parameter:
              </p>
              <BlockMath math="R = \left| \frac{1}{N} \sum_{j=1}^{N} e^{i\theta_j} \right|" />
              <p className="text-sm text-muted mt-4">
                <InlineMath math="R = 0" /> indicates complete incoherence,{" "}
                <InlineMath math="R = 1" /> indicates perfect synchrony. All
                intermediate values define the regime boundaries.
              </p>
            </div>

            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-4">
                Critical Coupling
              </h3>
              <p className="text-sm text-muted mb-4">
                The system undergoes a phase transition at the critical coupling
                strength:
              </p>
              <BlockMath math="K_c = \frac{2\sigma_\omega}{\pi}" />
              <p className="text-sm text-muted mt-4">
                Below <InlineMath math="K_c" />, the oscillators remain
                incoherent. Above <InlineMath math="K_c" />, a macroscopic
                fraction synchronizes spontaneously. This bifurcation separates
                pathological (turbulent) from functional (cascade/coherent)
                operation.
              </p>
            </div>
          </div>
        </div>
      </SectionLayout>

      {/* Five Regimes */}
      <SectionLayout id="regimes">
        <div className="max-w-5xl mx-auto">
          <h2 className="section-heading text-center">
            The Five Operational Regimes
          </h2>
          <p className="section-subheading text-center mx-auto">
            Every neural state maps to exactly one regime, classified by{" "}
            <InlineMath math="R" /> boundaries and structural factor values.
          </p>
          <div className="space-y-6 mt-12">
            {[
              {
                regime: "turbulent",
                name: "Turbulent",
                range: "R < 0.3",
                structural: "S \\approx 0",
                brain: "Seizure prodrome, severe delirium, deep anesthesia washout",
                physical: "Fully developed turbulence, uncorrelated spin glass",
                description:
                  "Complete desynchronization. No macroscopic order emerges. Individual oscillators run at their natural frequencies with no mutual entrainment. The system dissipates maximal energy with no coherent output.",
              },
              {
                regime: "aperture",
                name: "Aperture",
                range: "0.3 \\leq R < 0.5",
                structural: "S \\approx 0.2",
                brain: "REM sleep, psychedelic states, creative divergent thinking",
                physical: "Partial synchrony onset, cluster formation in Josephson arrays",
                description:
                  "Selective gating begins. Small clusters of oscillators lock transiently, creating apertures through which specific frequency bands pass. This regime enables flexible filtering without global coherence.",
              },
              {
                regime: "cascade",
                name: "Cascade",
                range: "0.5 \\leq R < 0.8",
                structural: "S \\approx 0.5",
                brain: "N1/N2 sleep, relaxed wakefulness, default mode network",
                physical: "Cooperative synchronization, critical cascades, power-law avalanches",
                description:
                  "Cooperative synchronization propagates through the network. Macroscopic clusters form and dissolve on intermediate timescales. The system operates near criticality, maximizing dynamic range and information transmission.",
              },
              {
                regime: "coherent",
                name: "Coherent",
                range: "0.8 \\leq R < 0.95",
                structural: "S \\approx 0.8",
                brain: "Alert wakefulness, focused attention, N3 deep sleep",
                physical: "Laser above threshold, superfluid phase, Bose-Einstein condensate",
                description:
                  "Healthy baseline operation. The majority of oscillators are entrained to a common frequency. Stable macroscopic rhythms support reliable information processing and motor coordination.",
              },
              {
                regime: "locked",
                name: "Phase-Locked",
                range: "R \\geq 0.95",
                structural: "S \\to 1",
                brain: "Tonic-clonic seizure, catatonia, status epilepticus",
                physical: "Rigid body rotation, ferromagnetic saturation",
                description:
                  "Hypersynchrony. Nearly all oscillators are phase-locked. The system loses flexibility and cannot modulate its output. Pathological in neural context: epileptic seizures represent this regime.",
              },
            ].map((item, i) => (
              <motion.div
                key={item.name}
                className="card"
                variants={fadeUp}
                custom={i}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
              >
                <div className="flex items-start gap-4 md:flex-col">
                  <div className="flex-shrink-0 w-32 md:w-full">
                    <RegimeBadge regime={item.regime} className="mb-2" />
                    <div className="text-xs text-muted font-mono mt-2">
                      <InlineMath math={item.range} />
                    </div>
                    <div className="text-xs text-muted font-mono mt-1">
                      <InlineMath math={item.structural} />
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-dark dark:text-light leading-relaxed mb-3">
                      {item.description}
                    </p>
                    <div className="grid grid-cols-2 gap-4 md:grid-cols-1">
                      <div>
                        <span className="text-xs font-semibold uppercase tracking-wider text-muted">
                          Brain States
                        </span>
                        <p className="text-sm text-muted mt-1">{item.brain}</p>
                      </div>
                      <div>
                        <span className="text-xs font-semibold uppercase tracking-wider text-muted">
                          Physical Analogues
                        </span>
                        <p className="text-sm text-muted mt-1">
                          {item.physical}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </SectionLayout>

      {/* Sleep Architecture */}
      <SectionLayout
        id="sleep"
        className="bg-dark/[0.02] dark:bg-light/[0.02]"
      >
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Sleep Architecture</h2>
          <p className="section-subheading">
            Sleep stages map systematically onto the regime classification.
            The 90-minute ultradian cycle traces a periodic orbit through
            regime space.
          </p>

          <div className="card mt-8">
            <h3 className="font-semibold text-dark dark:text-light mb-4">
              Stage-to-Regime Mapping
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-dark/10 dark:border-light/10">
                    <th className="text-left py-3 px-4 text-muted font-semibold">
                      Sleep Stage
                    </th>
                    <th className="text-left py-3 px-4 text-muted font-semibold">
                      Regime
                    </th>
                    <th className="text-left py-3 px-4 text-muted font-semibold">
                      R Range
                    </th>
                    <th className="text-left py-3 px-4 text-muted font-semibold">
                      Dominant Band
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    {
                      stage: "N3 (Deep Sleep)",
                      regime: "locked",
                      r: "R > 0.9",
                      band: "Delta (0.5\u20134 Hz)",
                    },
                    {
                      stage: "W (Wakefulness)",
                      regime: "coherent",
                      r: "0.8 < R < 0.9",
                      band: "Alpha/Beta (8\u201330 Hz)",
                    },
                    {
                      stage: "N1 (Light Sleep)",
                      regime: "cascade",
                      r: "0.6 < R < 0.8",
                      band: "Theta (4\u20138 Hz)",
                    },
                    {
                      stage: "N2 (Spindle Sleep)",
                      regime: "cascade",
                      r: "0.5 < R < 0.7",
                      band: "Sigma (12\u201315 Hz)",
                    },
                    {
                      stage: "REM",
                      regime: "turbulent",
                      r: "R < 0.5",
                      band: "Theta (4\u20138 Hz)",
                    },
                  ].map((row) => (
                    <tr
                      key={row.stage}
                      className="border-b border-dark/5 dark:border-light/5"
                    >
                      <td className="py-3 px-4 text-dark dark:text-light font-medium">
                        {row.stage}
                      </td>
                      <td className="py-3 px-4">
                        <RegimeBadge regime={row.regime} />
                      </td>
                      <td className="py-3 px-4 font-mono text-muted">
                        {row.r}
                      </td>
                      <td className="py-3 px-4 text-muted">{row.band}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6 mt-8 md:grid-cols-1">
            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                R Ordering
              </h3>
              <p className="text-sm text-muted mb-4">
                The order parameter preserves a strict ordering across all
                epochs:
              </p>
              <BlockMath math="R_{\text{N3}} > R_{\text{W}} > R_{\text{N1}} > R_{\text{N2}} > R_{\text{REM}}" />
              <p className="text-sm text-muted mt-4">
                This ordering is validated across all 500 epochs in the test
                dataset. N3 achieves near-unity synchronization (delta
                dominance), while REM shows maximal desynchronization.
              </p>
            </div>
            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Ultradian Cycling
              </h3>
              <p className="text-sm text-muted mb-4">
                The ~90-minute sleep cycle is a periodic orbit in regime space:
              </p>
              <BlockMath math="\gamma(t) : [0, T_{\text{ultradian}}] \to \mathcal{R}" />
              <p className="text-sm text-muted mt-4">
                The trajectory descends from coherent (W) through cascade
                (N1/N2) to locked (N3), then jumps to turbulent/aperture (REM)
                before returning. Band power decomposition confirms delta
                dominance in N3 and theta dominance in REM.
              </p>
            </div>
          </div>

          <div className="mt-6">
            <div className="flex gap-3 flex-wrap">
              <ValidationBadge label="Sleep claims validated" value="6/6" />
              <ValidationBadge label="N3-REM separation" value="established" />
              <ValidationBadge label="R ordering" value="all epochs" />
            </div>
          </div>
        </div>
      </SectionLayout>

      {/* Critical Coupling */}
      <SectionLayout id="critical-coupling">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Critical Coupling and Bifurcation</h2>
          <p className="section-subheading">
            The transition from incoherence to synchrony occurs at a sharp
            bifurcation point determined analytically.
          </p>

          <div className="grid grid-cols-2 gap-6 mt-8 md:grid-cols-1">
            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Bifurcation Point
              </h3>
              <p className="text-sm text-muted mb-4">
                For a Lorentzian frequency distribution with half-width{" "}
                <InlineMath math="\sigma_\omega" />, the critical coupling is:
              </p>
              <BlockMath math="K_c = \frac{2\sigma_\omega}{\pi}" />
              <p className="text-sm text-muted mt-4">
                Below <InlineMath math="K_c" />, the only stable state is{" "}
                <InlineMath math="R = 0" />
                (incoherent). Above <InlineMath math="K_c" />, a nonzero{" "}
                <InlineMath math="R" /> branch appears via supercritical
                pitchfork bifurcation.
              </p>
            </div>
            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Finite-Size Scaling
              </h3>
              <p className="text-sm text-muted mb-4">
                For finite <InlineMath math="N" />, the transition is smoothed.
                The order parameter scales as:
              </p>
              <BlockMath math="R \sim N^{-1/2} \quad \text{for } K < K_c" />
              <BlockMath math="R \sim \left(\frac{K - K_c}{K_c}\right)^{1/2} \quad \text{for } K > K_c" />
              <p className="text-sm text-muted mt-4">
                The analytical prediction is validated against numerical
                simulation across system sizes{" "}
                <InlineMath math="N = 50" /> to{" "}
                <InlineMath math="N = 10{,}000" />.
              </p>
            </div>
          </div>
        </div>
      </SectionLayout>

      {/* Consciousness Window */}
      <SectionLayout
        id="consciousness"
        className="bg-dark/[0.02] dark:bg-light/[0.02]"
      >
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">The Consciousness Window</h2>
          <p className="section-subheading">
            Consciousness requires temporal overlap between perception decay and
            thought decay.
          </p>

          <div className="card mt-8">
            <BlockMath math="\mathcal{C} = P_{\text{decay}} \cap T_{\text{decay}}" />
            <p className="text-sm text-muted mt-6 leading-relaxed">
              The consciousness window{" "}
              <InlineMath math="\mathcal{C}" /> is defined as the temporal
              intersection of perceptual decay{" "}
              <InlineMath math="P_{\text{decay}}" /> (the fading of sensory
              input) and thought decay{" "}
              <InlineMath math="T_{\text{decay}}" /> (the fading of internal
              representation). When these two processes overlap in time,
              conscious experience arises. Outside this window, the system
              operates in either purely sensory (reflexive) or purely internal
              (unconscious processing) modes.
            </p>
            <p className="text-sm text-muted mt-4 leading-relaxed">
              This window is maximized in the coherent regime (alert
              wakefulness) and collapses in both the turbulent regime (where
              perceptual integration fails) and the phase-locked regime (where
              internal dynamics are frozen).
            </p>
          </div>
        </div>
      </SectionLayout>

      {/* Variance Minimization */}
      <SectionLayout id="variance">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Variance Minimization</h2>
          <p className="section-subheading">
            The free energy principle yields exact predictions for variance
            scaling.
          </p>

          <div className="grid grid-cols-2 gap-6 mt-8 md:grid-cols-1">
            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Free Energy
              </h3>
              <BlockMath math="F = k_B T \cdot \sigma^2" />
              <p className="text-sm text-muted mt-4">
                The free energy of the partition is proportional to the variance
                of the order parameter fluctuations. The system minimizes{" "}
                <InlineMath math="F" /> by reducing{" "}
                <InlineMath math="\sigma^2" />, driving toward increased
                synchronization.
              </p>
            </div>
            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Variance Floor
              </h3>
              <BlockMath math="\sigma^2_{\min} = \frac{k_B T}{K}" />
              <p className="text-sm text-muted mt-4">
                The variance cannot be reduced below the thermal floor set by
                the ratio of temperature to coupling. The scaling slope is
                exactly <InlineMath math="-1" /> on a log-log plot of{" "}
                <InlineMath math="\sigma^2" /> vs{" "}
                <InlineMath math="K" />.
              </p>
            </div>
          </div>

          <div className="mt-6">
            <ValidationBadge label="Variance scaling slope" value="-1.0 (exact)" />
          </div>
        </div>
      </SectionLayout>

      {/* Figures */}
      <SectionLayout
        id="figures"
        className="bg-dark/[0.02] dark:bg-light/[0.02]"
      >
        <div className="max-w-5xl mx-auto">
          <h2 className="section-heading text-center">Figures</h2>
          <p className="section-subheading text-center mx-auto">
            Six panels summarizing the key results of the regime classification
            framework.
          </p>
          <div className="grid grid-cols-3 gap-6 mt-12 md:grid-cols-2 sm:grid-cols-1">
            <FigurePlaceholder
              panel={1}
              description="Kuramoto order parameter R vs coupling strength K, showing the supercritical bifurcation at K_c"
            />
            <FigurePlaceholder
              panel={2}
              description="Five-regime phase diagram with R boundaries and representative time series for each regime"
            />
            <FigurePlaceholder
              panel={3}
              description="Sleep hypnogram overlaid with R trajectory, showing ultradian cycling through regime space"
            />
            <FigurePlaceholder
              panel={4}
              description="Band power decomposition across sleep stages: delta, theta, alpha, sigma, beta"
            />
            <FigurePlaceholder
              panel={5}
              description="Variance scaling: log-log plot of sigma^2 vs K with slope = -1.0"
            />
            <FigurePlaceholder
              panel={6}
              description="Consciousness window C = P_decay intersect T_decay as a function of regime"
            />
          </div>
        </div>
      </SectionLayout>

      {/* Navigation */}
      <SectionLayout>
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading text-center">Continue Reading</h2>
          <div className="grid grid-cols-2 gap-6 mt-8 md:grid-cols-1">
            <Link href="/apertures" className="block card group cursor-pointer">
              <div className="flex gap-2 mb-3">
                <RegimeBadge regime="aperture" />
                <RegimeBadge regime="cascade" />
              </div>
              <h3 className="text-lg font-semibold text-dark dark:text-light mb-2 group-hover:text-primary dark:group-hover:text-primaryDark transition-colors">
                Geometric Apertures
              </h3>
              <p className="text-sm text-muted">
                Zero-work selectivity from categorical constraints. Monopole,
                dipole, and quadrupole drug taxonomies.
              </p>
            </Link>
            <Link href="/computing" className="block card group cursor-pointer">
              <div className="flex gap-2 mb-3">
                <RegimeBadge regime="coherent" />
                <RegimeBadge regime="locked" />
              </div>
              <h3 className="text-lg font-semibold text-dark dark:text-light mb-2 group-hover:text-primary dark:group-hover:text-primaryDark transition-colors">
                Operator Trajectories
              </h3>
              <p className="text-sm text-muted">
                A formal language for bounded phase-space computing. Partition
                coordinates and the pNPL type system.
              </p>
            </Link>
          </div>
          <div className="text-center mt-8">
            <Link
              href="/"
              className="text-primary dark:text-primaryDark hover:underline text-sm"
            >
              &larr; Back to Home
            </Link>
          </div>
        </div>
      </SectionLayout>
    </>
  );
}

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

export default function Apertures() {
  return (
    <>
      <Head>
        <title>Geometric Apertures | Neural Partition Language</title>
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
              Paper II
            </motion.p>
            <motion.h1
              className="text-5xl font-bold text-dark dark:text-light leading-tight mb-6 xl:text-4xl md:text-3xl sm:text-2xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              Geometric{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
                Apertures
              </span>
            </motion.h1>
            <motion.p
              className="text-lg text-muted max-w-2xl mx-auto mb-8 md:text-base"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              Zero-Work Selectivity from Categorical Constraints
            </motion.p>
            <motion.div
              className="flex gap-3 justify-center flex-wrap"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <ValidationBadge label="Aperture accuracy" value="63.6%" />
              <ValidationBadge label="Breadth ordering" value="validated" />
              <ValidationBadge label="Response convergence" value="~60%" />
              <ValidationBadge label="Hill correlation" value="confirmed" />
            </motion.div>
          </div>
        </div>
      </section>

      {/* Introduction */}
      <SectionLayout id="introduction">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Introduction</h2>
          <p className="section-subheading">
            A puzzle at the heart of psychopharmacology: drugs with completely
            different molecular mechanisms&mdash;SSRIs blocking serotonin
            reuptake, SNRIs blocking both serotonin and norepinephrine, TCAs
            hitting five or more targets&mdash;all produce the same ~60%
            response rate.
          </p>
          <p className="text-muted mt-6 leading-relaxed">
            We show that this convergence is not coincidental but necessary.
            Apertures are topological constraints on the phase space partition
            that impose selectivity at zero thermodynamic work. The drug does
            not push the system into a new state by expending energy; instead,
            it reshapes the geometry of accessible states. Different aperture
            types (monopole, dipole, quadrupole) represent categorically
            distinct constraint geometries, yet they all funnel the system
            toward the same structural factor value&mdash;explaining the
            universal ~60% response rate.
          </p>
        </div>
      </SectionLayout>

      {/* Multipole Taxonomy */}
      <SectionLayout
        id="multipole"
        className="bg-dark/[0.02] dark:bg-light/[0.02]"
      >
        <div className="max-w-5xl mx-auto">
          <h2 className="section-heading">Multipole Taxonomy</h2>
          <p className="section-subheading">
            Apertures are classified by their multipole order{" "}
            <InlineMath math="\ell" />, which determines the angular structure
            of the constraint field.
          </p>

          <div className="grid grid-cols-3 gap-6 mt-12 md:grid-cols-1">
            {[
              {
                order: "0",
                name: "Monopole",
                symbol: "\u2113 = 0",
                class: "SSRI",
                example: "Escitalopram (SERT-only)",
                field: "|E| \\propto 1/r^2",
                description:
                  "Single-target selectivity. The constraint field is spherically symmetric. One receptor is blocked with high affinity; all others are unaffected. Maximum selectivity, minimum breadth.",
                color: "from-regime-aperture to-regime-cascade",
              },
              {
                order: "1",
                name: "Dipole",
                symbol: "\u2113 = 1",
                class: "SNRI",
                example: "Duloxetine (SERT + NET)",
                field: "|E| \\propto 1/r^3",
                description:
                  "Dual-target selectivity. The constraint has a directional axis. Two receptors are blocked with comparable affinity, creating an anisotropic aperture that filters along a preferred dimension.",
                color: "from-regime-cascade to-regime-coherent",
              },
              {
                order: "2",
                name: "Quadrupole",
                symbol: "\u2113 = 2",
                class: "TCA",
                example: "Amitriptyline (5+ targets)",
                field: "|E| \\propto 1/r^4",
                description:
                  "Multi-target selectivity. The constraint field has four lobes. Five or more receptors are affected, creating a complex aperture geometry. Maximum breadth, minimum selectivity.",
                color: "from-regime-coherent to-regime-locked",
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
                <div
                  className={`w-10 h-10 rounded-lg bg-gradient-to-br ${item.color} flex items-center justify-center text-white font-bold text-sm mb-4`}
                >
                  {item.symbol}
                </div>
                <h3 className="text-lg font-semibold text-dark dark:text-light mb-1">
                  {item.name}
                </h3>
                <span className="text-xs font-mono text-primary dark:text-primaryDark">
                  {item.class}
                </span>
                <p className="text-sm text-muted mt-3 leading-relaxed">
                  {item.description}
                </p>
                <div className="mt-4 pt-4 border-t border-dark/5 dark:border-light/5">
                  <p className="text-xs text-muted">
                    <span className="font-semibold">Example:</span>{" "}
                    {item.example}
                  </p>
                  <div className="mt-2">
                    <InlineMath math={item.field} />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="card mt-8">
            <h3 className="font-semibold text-dark dark:text-light mb-3">
              General Field Equation
            </h3>
            <BlockMath math="|E_\ell| \propto \frac{1}{r^{\ell + 2}}" />
            <p className="text-sm text-muted mt-4">
              The constraint field decays as{" "}
              <InlineMath math="r^{-(\ell+2)}" />, where{" "}
              <InlineMath math="r" /> is the distance in receptor space.
              Higher-order multipoles have steeper falloff, meaning their
              influence is more localized despite affecting more targets.
            </p>
          </div>
        </div>
      </SectionLayout>

      {/* Drug Binding Profiles */}
      <SectionLayout id="binding">
        <div className="max-w-5xl mx-auto">
          <h2 className="section-heading">Drug Binding Profiles</h2>
          <p className="section-subheading">
            Eleven antidepressants spanning all three multipole orders, with
            inhibition constants{" "}
            <InlineMath math="K_i" /> from published binding assays.
          </p>

          <div className="card mt-8 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-dark/10 dark:border-light/10">
                  <th className="text-left py-3 px-4 text-muted font-semibold">
                    Drug
                  </th>
                  <th className="text-left py-3 px-4 text-muted font-semibold">
                    Class
                  </th>
                  <th className="text-left py-3 px-4 text-muted font-semibold">
                    Order
                  </th>
                  <th className="text-left py-3 px-4 text-muted font-semibold">
                    Primary Target
                  </th>
                  <th className="text-left py-3 px-4 text-muted font-semibold">
                    Selectivity Ratio
                  </th>
                </tr>
              </thead>
              <tbody>
                {[
                  { drug: "Escitalopram", cls: "SSRI", order: "0", target: "SERT", ratio: "> 1000" },
                  { drug: "Sertraline", cls: "SSRI", order: "0", target: "SERT", ratio: "> 100" },
                  { drug: "Fluoxetine", cls: "SSRI", order: "0", target: "SERT", ratio: "> 100" },
                  { drug: "Paroxetine", cls: "SSRI", order: "0", target: "SERT", ratio: "> 100" },
                  { drug: "Citalopram", cls: "SSRI", order: "0", target: "SERT", ratio: "> 500" },
                  { drug: "Venlafaxine", cls: "SNRI", order: "1", target: "SERT + NET", ratio: "~30" },
                  { drug: "Duloxetine", cls: "SNRI", order: "1", target: "SERT + NET", ratio: "~10" },
                  { drug: "Desvenlafaxine", cls: "SNRI", order: "1", target: "SERT + NET", ratio: "~10" },
                  { drug: "Amitriptyline", cls: "TCA", order: "2", target: "SERT + NET + 5HT\u2082 + H\u2081 + mACh", ratio: "< 5" },
                  { drug: "Nortriptyline", cls: "TCA", order: "2", target: "NET + SERT + 5HT\u2082 + H\u2081", ratio: "< 10" },
                  { drug: "Clomipramine", cls: "TCA", order: "2", target: "SERT + NET + 5HT\u2082 + H\u2081 + mACh", ratio: "< 5" },
                ].map((row) => (
                  <tr
                    key={row.drug}
                    className="border-b border-dark/5 dark:border-light/5"
                  >
                    <td className="py-3 px-4 text-dark dark:text-light font-medium">
                      {row.drug}
                    </td>
                    <td className="py-3 px-4 text-muted">{row.cls}</td>
                    <td className="py-3 px-4 font-mono text-muted">
                      <InlineMath math={`\\ell = ${row.order}`} />
                    </td>
                    <td className="py-3 px-4 text-muted text-xs">
                      {row.target}
                    </td>
                    <td className="py-3 px-4 font-mono text-muted">
                      {row.ratio}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="card mt-6">
            <h3 className="font-semibold text-dark dark:text-light mb-3">
              Selectivity Ratio
            </h3>
            <BlockMath math="\text{Selectivity} = \frac{K_i^{\text{secondary}}}{K_i^{\text{primary}}}" />
            <p className="text-sm text-muted mt-4">
              High selectivity ratios ({">"}100) indicate monopole geometry;
              low ratios ({"<"}10) indicate quadrupole. The breadth ordering{" "}
              <InlineMath math="\text{TCA} > \text{SNRI} > \text{SSRI}" /> is
              validated across all 11 compounds.
            </p>
          </div>
        </div>
      </SectionLayout>

      {/* Cross-Modal Equivalence */}
      <SectionLayout
        id="equivalence"
        className="bg-dark/[0.02] dark:bg-light/[0.02]"
      >
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Cross-Modal Equivalence</h2>
          <p className="section-subheading">
            Despite different mechanisms and multipole orders, all
            antidepressants converge to the same response rate.
          </p>

          <div className="grid grid-cols-2 gap-6 mt-8 md:grid-cols-1">
            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Universal Response Rate
              </h3>
              <div className="text-4xl font-bold text-primary dark:text-primaryDark mb-2">
                ~60%
              </div>
              <p className="text-sm text-muted leading-relaxed">
                Across SSRIs, SNRIs, and TCAs, clinical response rates cluster
                around 60%. The cross-class variance is remarkably low:
              </p>
              <BlockMath math="\sigma_{\text{cross-class}} = 0.005" />
            </div>
            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Structural Factor Determines Response
              </h3>
              <p className="text-sm text-muted leading-relaxed">
                The response rate is determined not by the aperture type
                (monopole, dipole, quadrupole) but by the structural factor{" "}
                <InlineMath math="S" /> of the target regime. Since all drugs
                aim to shift the system from the same pathological regime to the
                same healthy regime, the structural factor is identical
                regardless of mechanism.
              </p>
              <p className="text-sm text-muted mt-3 leading-relaxed">
                This explains the paradox: different keys open different locks,
                but all doors lead to the same room.
              </p>
            </div>
          </div>
        </div>
      </SectionLayout>

      {/* Regime Transition */}
      <SectionLayout id="transition">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Regime Transition via Drug Action</h2>
          <p className="section-subheading">
            Drugs increase the effective coupling{" "}
            <InlineMath math="K" />, driving the system from turbulent toward
            coherent.
          </p>

          <div className="grid grid-cols-2 gap-6 mt-8 md:grid-cols-1">
            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Entropy Change
              </h3>
              <BlockMath math="\Delta S = S_{\text{post}} - S_{\text{pre}}" />
              <p className="text-sm text-muted mt-4">
                Drug administration reduces the partition entropy by increasing
                synchronization. The system transitions from high-entropy
                (turbulent, many accessible microstates) to low-entropy
                (coherent, fewer but more organized microstates).
              </p>
              <div className="flex gap-3 mt-4">
                <RegimeBadge regime="turbulent" />
                <span className="text-muted">&rarr;</span>
                <RegimeBadge regime="coherent" />
              </div>
            </div>
            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Dose-Response via Hill Equation
              </h3>
              <BlockMath math="E = \frac{E_{\max} \cdot D^{n_H}}{D^{n_H} + \text{EC}_{50}^{n_H}}" />
              <p className="text-sm text-muted mt-4">
                The Hill coefficient{" "}
                <InlineMath math="n_H" /> is determined by the aperture order:
              </p>
              <BlockMath math="n_H = \ell + 1" />
              <p className="text-sm text-muted mt-3">
                Monopoles (<InlineMath math="n_H = 1" />) give hyperbolic
                dose-response. Quadrupoles (<InlineMath math="n_H = 3" />) give
                sigmoidal dose-response with steeper transition, consistent with
                the narrower therapeutic windows of TCAs.
              </p>
            </div>
          </div>
        </div>
      </SectionLayout>

      {/* Enzyme Catalysis */}
      <SectionLayout
        id="enzymes"
        className="bg-dark/[0.02] dark:bg-light/[0.02]"
      >
        <div className="max-w-5xl mx-auto">
          <h2 className="section-heading">Enzyme Catalysis</h2>
          <p className="section-subheading">
            The aperture framework extends beyond neuropharmacology. Enzyme
            catalytic efficiency follows the same geometric constraints.
          </p>

          <div className="grid grid-cols-2 gap-6 mt-8 md:grid-cols-1">
            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Efficiency vs Partition Depth
              </h3>
              <p className="text-sm text-muted leading-relaxed">
                Catalytic efficiency{" "}
                <InlineMath math="k_{\text{cat}}/K_m" />{" "}
                anti-correlates with the partition depth{" "}
                <InlineMath math="d_{\text{cat}}" />. Enzymes operating near
                the diffusion limit (<InlineMath math="d_{\text{cat}} \to 0" />)
                achieve maximum efficiency by imposing minimal geometric
                constraint.
              </p>
              <p className="text-sm text-muted mt-3 leading-relaxed">
                Data from 12 enzymes in the BRENDA database confirms this
                relationship across three orders of magnitude in{" "}
                <InlineMath math="k_{\text{cat}}/K_m" />.
              </p>
            </div>
            <div className="card">
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Triple Equivalence
              </h3>
              <BlockMath math="S_{\text{osc}} = S_{\text{cat}} = S_{\text{part}}" />
              <p className="text-sm text-muted mt-4 leading-relaxed">
                The structural factor computed from oscillator synchronization,
                catalytic efficiency, and partition geometry all yield the same
                value. This triple equivalence confirms that apertures are a
                universal geometric phenomenon, not specific to neural systems.
              </p>
            </div>
          </div>

          <div className="card mt-6">
            <h3 className="font-semibold text-dark dark:text-light mb-3">
              Enzyme Dataset (BRENDA)
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-dark/10 dark:border-light/10">
                    <th className="text-left py-3 px-4 text-muted font-semibold">
                      Property
                    </th>
                    <th className="text-left py-3 px-4 text-muted font-semibold">
                      Value
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-dark/5 dark:border-light/5">
                    <td className="py-3 px-4 text-dark dark:text-light">
                      Enzymes analyzed
                    </td>
                    <td className="py-3 px-4 text-muted font-mono">12</td>
                  </tr>
                  <tr className="border-b border-dark/5 dark:border-light/5">
                    <td className="py-3 px-4 text-dark dark:text-light">
                      Efficiency range
                    </td>
                    <td className="py-3 px-4 text-muted font-mono">
                      <InlineMath math="10^4 - 10^8 \; M^{-1}s^{-1}" />
                    </td>
                  </tr>
                  <tr className="border-b border-dark/5 dark:border-light/5">
                    <td className="py-3 px-4 text-dark dark:text-light">
                      Diffusion limit
                    </td>
                    <td className="py-3 px-4 text-muted font-mono">
                      <InlineMath math="\sim 10^8 \; M^{-1}s^{-1}" />
                    </td>
                  </tr>
                  <tr className="border-b border-dark/5 dark:border-light/5">
                    <td className="py-3 px-4 text-dark dark:text-light">
                      Anti-correlation with{" "}
                      <InlineMath math="d_{\text{cat}}" />
                    </td>
                    <td className="py-3 px-4 text-muted font-mono">
                      Confirmed
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </SectionLayout>

      {/* Onset Delay */}
      <SectionLayout id="onset">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Onset Delay</h2>
          <p className="section-subheading">
            The model predicts therapeutic onset latency from aperture geometry.
          </p>

          <div className="card mt-8">
            <h3 className="font-semibold text-dark dark:text-light mb-3">
              Predicted Onset Time
            </h3>
            <BlockMath math="T_{\text{onset}} = \tau_{\text{adapt}} \cdot f(n_{\text{targets}})" />
            <p className="text-sm text-muted mt-4 leading-relaxed">
              The onset delay <InlineMath math="T_{\text{onset}}" /> is the
              product of the adaptation timescale{" "}
              <InlineMath math="\tau_{\text{adapt}}" /> (determined by receptor
              desensitization kinetics) and a function of the number of
              targets{" "}
              <InlineMath math="n_{\text{targets}}" />. Monopole drugs (single
              target) have the fastest onset because only one receptor population
              must adapt. Quadrupole drugs (multiple targets) require sequential
              adaptation across receptor populations, leading to longer onset.
            </p>
            <div className="grid grid-cols-3 gap-4 mt-6 md:grid-cols-1">
              {[
                { cls: "SSRI", onset: "2\u20134 weeks", targets: "1" },
                { cls: "SNRI", onset: "2\u20136 weeks", targets: "2" },
                { cls: "TCA", onset: "4\u20138 weeks", targets: "5+" },
              ].map((item) => (
                <div
                  key={item.cls}
                  className="text-center p-4 rounded-lg bg-dark/[0.03] dark:bg-light/[0.03]"
                >
                  <div className="text-sm font-semibold text-dark dark:text-light">
                    {item.cls}
                  </div>
                  <div className="text-lg font-bold text-primary dark:text-primaryDark mt-1">
                    {item.onset}
                  </div>
                  <div className="text-xs text-muted mt-1">
                    {item.targets} target{item.targets !== "1" ? "s" : ""}
                  </div>
                </div>
              ))}
            </div>
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
            Six panels illustrating aperture geometry, drug binding profiles,
            and cross-modal equivalence.
          </p>
          <div className="grid grid-cols-3 gap-6 mt-12 md:grid-cols-2 sm:grid-cols-1">
            <FigurePlaceholder
              panel={1}
              description="Multipole field geometry: monopole, dipole, and quadrupole constraint fields in receptor space"
            />
            <FigurePlaceholder
              panel={2}
              description="Drug binding profiles: Ki values for 11 antidepressants across receptor targets"
            />
            <FigurePlaceholder
              panel={3}
              description="Cross-modal convergence: response rates by drug class, showing ~60% convergence with low cross-class variance"
            />
            <FigurePlaceholder
              panel={4}
              description="Dose-response curves: Hill equation fits for monopole (n_H=1), dipole (n_H=2), quadrupole (n_H=3)"
            />
            <FigurePlaceholder
              panel={5}
              description="Enzyme catalytic efficiency vs partition depth for 12 BRENDA enzymes, showing anti-correlation"
            />
            <FigurePlaceholder
              panel={6}
              description="Onset delay: predicted vs reported therapeutic onset across drug classes"
            />
          </div>
        </div>
      </SectionLayout>

      {/* Navigation */}
      <SectionLayout>
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading text-center">Continue Reading</h2>
          <div className="grid grid-cols-2 gap-6 mt-8 md:grid-cols-1">
            <Link href="/regimes" className="block card group cursor-pointer">
              <div className="flex gap-2 mb-3">
                <RegimeBadge regime="turbulent" />
                <RegimeBadge regime="cascade" />
                <RegimeBadge regime="coherent" />
              </div>
              <h3 className="text-lg font-semibold text-dark dark:text-light mb-2 group-hover:text-primary dark:group-hover:text-primaryDark transition-colors">
                Regime Classification
              </h3>
              <p className="text-sm text-muted">
                From thermodynamic axioms to sleep architecture. Kuramoto
                synchronization and five operational regimes.
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

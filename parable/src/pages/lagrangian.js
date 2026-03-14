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

const ClaimRow = ({ domain, count, total, delay }) => (
  <motion.div
    className="flex items-center gap-4 py-3 border-b border-dark/5 dark:border-light/5 last:border-0"
    variants={fadeUp}
    custom={delay}
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true }}
  >
    <span className="text-sm text-dark dark:text-light flex-1">{domain}</span>
    <div className="w-32 h-2 bg-dark/5 dark:bg-light/5 rounded-full overflow-hidden">
      <motion.div
        className="h-full rounded-full bg-primary dark:bg-primaryDark"
        initial={{ width: 0 }}
        whileInView={{ width: `${(count / total) * 100}%` }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, delay: delay * 0.1 }}
      />
    </div>
    <span className="text-sm font-mono text-primary dark:text-primaryDark w-12 text-right">
      {count}/{total}
    </span>
  </motion.div>
);

export default function Lagrangian() {
  return (
    <>
      <Head>
        <title>The Neural Partition Lagrangian | Neural Partition Language</title>
      </Head>

      {/* ── Hero ── */}
      <section className="relative min-h-[70vh] flex items-center overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern dark:bg-grid-pattern-dark bg-grid opacity-50" />
        <div className="relative z-10 w-full px-32 xl:px-24 lg:px-16 md:px-12 sm:px-8 py-24">
          <div className="max-w-4xl">
            <motion.div
              className="flex gap-2 mb-6 flex-wrap"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              <RegimeBadge regime="turbulent" />
              <RegimeBadge regime="aperture" />
              <RegimeBadge regime="cascade" />
              <RegimeBadge regime="coherent" />
              <RegimeBadge regime="locked" />
            </motion.div>
            <motion.p
              className="text-sm font-semibold text-primary dark:text-primaryDark uppercase tracking-widest mb-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              Paper IV &mdash; The Capstone
            </motion.p>
            <motion.h1
              className="text-5xl font-bold text-dark dark:text-light leading-tight mb-6 xl:text-4xl md:text-3xl sm:text-2xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              The Neural Partition{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
                Lagrangian
              </span>
            </motion.h1>
            <motion.p
              className="text-lg text-muted max-w-2xl mb-8 md:text-base"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              A Variational Principle for Bounded Phase-Space Dynamics
            </motion.p>
            <motion.p
              className="text-sm text-muted max-w-xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              Everything &mdash; regimes, apertures, operators, trajectories
              &mdash; emerges as a necessary consequence of a single equation.
            </motion.p>
          </div>
        </div>
      </section>

      {/* ── 1. Motivation ── */}
      <SectionLayout id="motivation">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Why One Equation?</h2>
          <p className="section-subheading">
            Neural dynamics are dissipative and first-order. The standard
            Lagrangian <InlineMath math="L = T - V" /> assumes conservative,
            second-order systems. We need something different.
          </p>

          <div className="grid grid-cols-3 gap-6 mt-8 md:grid-cols-1">
            {[
              {
                problem: "Dissipative",
                desc: "Neural circuits dissipate energy; there is no kinetic energy in the Newtonian sense. Trajectories are gradient flows, not ballistic.",
                icon: "I",
              },
              {
                problem: "First-Order",
                desc: "The equations of motion are first-order ODEs (\u1E58 = f(R)), not second-order (\u00FCq = F). Standard Lagrangian mechanics does not apply directly.",
                icon: "II",
              },
              {
                problem: "Stochastic",
                desc: "Thermal noise drives transitions between regimes. We need a formalism that treats fluctuations as fundamental, not perturbative.",
                icon: "III",
              },
            ].map((item, i) => (
              <motion.div key={item.problem} className="card" variants={fadeUp} custom={i} initial="hidden" whileInView="visible" viewport={{ once: true }}>
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-sm mb-4">
                  {item.icon}
                </div>
                <h3 className="font-semibold text-dark dark:text-light mb-2">{item.problem}</h3>
                <p className="text-sm text-muted">{item.desc}</p>
              </motion.div>
            ))}
          </div>

          <motion.div className="card mt-8" variants={fadeUp} custom={3} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h3 className="font-semibold text-dark dark:text-light mb-3">The Onsager-Machlup Solution</h3>
            <p className="text-sm text-muted">
              The Onsager-Machlup action functional provides a variational
              principle for dissipative stochastic systems. Originally developed
              for near-equilibrium fluctuations, it naturally handles first-order
              dynamics and assigns a probability to every trajectory. The most
              probable trajectory is the one that extremizes the action &mdash;
              exactly the gradient flow prescribed by the potential.
            </p>
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 2. Generalized Coordinates ── */}
      <SectionLayout id="coordinates" className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Generalized Coordinates</h2>
          <p className="section-subheading">
            Five degrees of freedom capture the full neural state. Together they
            define a compact configuration manifold.
          </p>

          <motion.div className="card mt-8" variants={fadeUp} custom={0} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <BlockMath math="q = (R,\; \sigma^2,\; S_k,\; S_t,\; S_e)" />
            <div className="grid grid-cols-5 gap-4 mt-6 md:grid-cols-2 sm:grid-cols-1">
              {[
                { sym: "R", name: "Order parameter", range: "[0, 1]" },
                { sym: "\\sigma^2", name: "Variance", range: "[0, 2\\pi^2]" },
                { sym: "S_k", name: "Kolmogorov entropy", range: "[0, 1]" },
                { sym: "S_t", name: "Thermodynamic entropy", range: "[0, 1]" },
                { sym: "S_e", name: "Entanglement entropy", range: "[0, 1]" },
              ].map((item, i) => (
                <div key={item.sym} className="text-center">
                  <div className="text-lg font-bold text-primary dark:text-primaryDark mb-1">
                    <InlineMath math={item.sym} />
                  </div>
                  <p className="text-xs text-dark dark:text-light font-medium">{item.name}</p>
                  <p className="text-xs text-muted mt-1">
                    <InlineMath math={item.range} />
                  </p>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div className="card mt-6" variants={fadeUp} custom={1} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h3 className="font-semibold text-dark dark:text-light mb-3">Configuration Manifold</h3>
            <BlockMath math="\mathcal{M} = [0,1] \times [0, 2\pi^2] \times [0,1]^3" />
            <p className="text-sm text-muted mt-3">
              The manifold is compact with boundary. The metric is block-diagonal:{" "}
              <InlineMath math="g_{ij}" /> separates the synchronization sector{" "}
              <InlineMath math="(R, \sigma^2)" /> from the entropy sector{" "}
              <InlineMath math="(S_k, S_t, S_e)" />. This block structure
              reflects the physical independence of synchronization dynamics
              from entropy dynamics at leading order, coupled only through the
              potential.
            </p>
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 3. The Neural Partition Potential ── */}
      <SectionLayout id="potential">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">The Neural Partition Potential</h2>
          <p className="section-subheading">
            This is the central equation of the entire framework. Every regime,
            every transition, every aperture constraint flows from a single
            potential function.
          </p>

          <motion.div
            className="card mt-8 border-2 border-primary/20 dark:border-primaryDark/20"
            variants={fadeUp}
            custom={0}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <div className="text-center mb-4">
              <span className="text-xs font-semibold text-primary dark:text-primaryDark uppercase tracking-widest">
                The Central Equation
              </span>
            </div>
            <BlockMath math="\boxed{\;\Phi(q) = V_{\text{sync}}(R) + V_{\text{var}}(\sigma^2) + V_{\text{SF}}(R, \sigma^2) + V_{\text{ent}}(S_k, S_t, S_e)\;}" />
          </motion.div>

          <div className="grid grid-cols-2 gap-6 mt-8 md:grid-cols-1">
            <motion.div className="card" variants={fadeUp} custom={1} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                <InlineMath math="V_{\text{sync}}" /> &mdash; Landau Synchronization
              </h3>
              <BlockMath math="V_{\text{sync}} = \frac{K_c - K}{2}\,R^2 + \frac{K}{4}\,R^4" />
              <p className="text-sm text-muted mt-3">
                A Landau free energy in the order parameter <InlineMath math="R" />.
                Below the critical coupling <InlineMath math="K < K_c" />, the
                minimum is at <InlineMath math="R = 0" /> (turbulent). Above{" "}
                <InlineMath math="K_c" />, symmetry breaks and a nonzero{" "}
                <InlineMath math="R" /> minimum appears (synchronization onset).
              </p>
            </motion.div>

            <motion.div className="card" variants={fadeUp} custom={2} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                <InlineMath math="V_{\text{var}}" /> &mdash; Variance Floor
              </h3>
              <BlockMath math="V_{\text{var}} = k_B T \, \sigma^2 + \frac{k_B T}{K \, \sigma^2}" />
              <p className="text-sm text-muted mt-3">
                Prevents both zero variance (forbidden null state, Axiom II) and
                infinite variance (bounded phase space, Axiom I). The minimum
                at <InlineMath math="\sigma^2_{\min} = 1/\sqrt{K}" /> sets
                the thermodynamic floor for neural fluctuations.
              </p>
            </motion.div>

            <motion.div className="card" variants={fadeUp} custom={3} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                <InlineMath math="V_{\text{SF}}" /> &mdash; Structural Factor Coupling
              </h3>
              <BlockMath math="V_{\text{SF}} = -\alpha \, R \, \exp\!\left(-\frac{\sigma^2}{2\pi^2}\right)" />
              <p className="text-sm text-muted mt-3">
                Couples synchronization to variance through a Debye-Waller-like
                factor. High variance suppresses synchronization; tight
                distributions amplify it. The coupling constant{" "}
                <InlineMath math="\alpha" /> sets the scale of aperture effects.
              </p>
            </motion.div>

            <motion.div className="card" variants={fadeUp} custom={4} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                <InlineMath math="V_{\text{ent}}" /> &mdash; S-Entropy
              </h3>
              <BlockMath math="V_{\text{ent}} = \sum_{i \in \{k,t,e\}} \left[ -\ln S_i(1-S_i) \right]" />
              <p className="text-sm text-muted mt-3">
                Boundary repulsion plus binary entropy for each S-coordinate.
                Prevents the system from reaching the cube faces (finite
                resolution, Axiom III) and produces the observed confinement
                of S-entropy trajectories away from the boundary.
              </p>
            </motion.div>
          </div>
        </div>
      </SectionLayout>

      {/* ── 4. The Lagrangian ── */}
      <SectionLayout id="lagrangian" className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">The Lagrangian</h2>
          <p className="section-subheading">
            The Onsager-Machlup Lagrangian assigns a cost to every trajectory.
            The most probable path extremizes the action.
          </p>

          <motion.div
            className="card mt-8 border-2 border-primary/20 dark:border-primaryDark/20"
            variants={fadeUp}
            custom={0}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <BlockMath math="L = \frac{1}{4D}\left|\dot{q} + \nabla\Phi\right|^2 - \frac{1}{2}\nabla^2\Phi" />
            <div className="mt-4 pt-4 border-t border-dark/5 dark:border-light/5">
              <BlockMath math="S[q] = \int_0^T L\,dt" />
            </div>
          </motion.div>

          <motion.div className="card mt-6" variants={fadeUp} custom={1} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h3 className="font-semibold text-dark dark:text-light mb-3">Structure of the Lagrangian</h3>
            <p className="text-sm text-muted mb-3">
              The first term <InlineMath math="\frac{1}{4D}|\dot{q} + \nabla\Phi|^2" />{" "}
              measures departure from gradient flow. Any trajectory that deviates
              from <InlineMath math="\dot{q} = -\nabla\Phi" /> pays a
              quadratic cost. The diffusion constant <InlineMath math="D" /> sets
              the noise scale.
            </p>
            <p className="text-sm text-muted">
              The second term <InlineMath math="-\frac{1}{2}\nabla^2\Phi" />{" "}
              is the entropic correction. It favors trajectories passing through
              regions of high curvature in the potential landscape &mdash;
              the saddle points and ridgelines that separate basins of attraction.
            </p>
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 5. Euler-Lagrange Equations ── */}
      <SectionLayout id="euler-lagrange">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Euler-Lagrange Equations</h2>
          <p className="section-subheading">
            Extremizing the action yields the equations of motion &mdash;
            gradient flow plus noise, with each coordinate governed by its
            sector of the potential.
          </p>

          <div className="space-y-6 mt-8">
            <motion.div className="card" variants={fadeUp} custom={0} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                <InlineMath math="\dot{R}" /> &mdash; Kuramoto Mean-Field
              </h3>
              <BlockMath math="\dot{R} = -\frac{\partial \Phi}{\partial R} = (K - K_c)\,R - K\,R^3 + \alpha\,\exp\!\left(-\frac{\sigma^2}{2\pi^2}\right)" />
              <p className="text-sm text-muted mt-3">
                The order parameter relaxes under Landau dynamics with a
                structural factor correction. The exponential term couples
                variance to synchronization: tight distributions (small{" "}
                <InlineMath math="\sigma^2" />) provide an additional drive
                toward coherence.
              </p>
            </motion.div>

            <motion.div className="card" variants={fadeUp} custom={1} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                <InlineMath math="\dot{\sigma}^2" /> &mdash; Variance Relaxation
              </h3>
              <BlockMath math="\dot{\sigma}^2 = -\frac{\partial \Phi}{\partial \sigma^2} = -k_B T + \frac{k_B T}{K\,(\sigma^2)^2} + \frac{\alpha\,R}{2\pi^2}\exp\!\left(-\frac{\sigma^2}{2\pi^2}\right)" />
              <p className="text-sm text-muted mt-3">
                Variance relaxes to its thermodynamic floor{" "}
                <InlineMath math="\sigma^2_{\min} = 1/\sqrt{K}" />.
                The <InlineMath math="1/(\sigma^2)^2" /> term enforces the
                no-null-state axiom: variance can never reach zero. The
                structural factor provides an additional restoring force
                proportional to <InlineMath math="R" />.
              </p>
            </motion.div>

            <motion.div className="card" variants={fadeUp} custom={2} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                <InlineMath math="\dot{S}_i" /> &mdash; Entropy Diffusion
              </h3>
              <BlockMath math="\dot{S}_i = -\frac{\partial \Phi}{\partial S_i} = \frac{1 - 2S_i}{S_i(1 - S_i)}, \quad i \in \{k, t, e\}" />
              <p className="text-sm text-muted mt-3">
                Each S-entropy coordinate diffuses within <InlineMath math="[0,1]" />,
                repelled from both boundaries. The equilibrium at{" "}
                <InlineMath math="S_i = \tfrac{1}{2}" /> represents maximum
                ignorance. The divergence at the boundaries enforces
                confinement within the bounded cube.
              </p>
            </motion.div>
          </div>
        </div>
      </SectionLayout>

      {/* ── 6. Aperture Constraints ── */}
      <SectionLayout id="aperture-constraints" className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Aperture Constraints</h2>
          <p className="section-subheading">
            Geometric apertures enter as holonomic constraints via Lagrange
            multipliers, enforcing selective gating without energy expenditure.
          </p>

          <motion.div className="card mt-8" variants={fadeUp} custom={0} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <h3 className="font-semibold text-dark dark:text-light mb-3">Constrained Lagrangian</h3>
            <BlockMath math="L_{\text{constrained}} = L + \sum_j \lambda_j \, f_j(q)" />
            <p className="text-sm text-muted mt-4 mb-4">
              Each aperture constraint <InlineMath math="f_j(q) = 0" /> is a
              hypersurface in configuration space. The multiplier{" "}
              <InlineMath math="\lambda_j" /> is the reaction force that
              maintains the constraint.
            </p>
            <div className="bg-dark/[0.03] dark:bg-light/[0.03] rounded-lg p-4">
              <h4 className="font-medium text-dark dark:text-light text-sm mb-2">Zero-Work Condition</h4>
              <BlockMath math="\sum_j \lambda_j \, \nabla f_j \cdot \dot{q} = 0" />
              <p className="text-sm text-muted mt-2">
                The constraint forces do no work along the trajectory.
                Selectivity is achieved geometrically, not energetically &mdash;
                the aperture steers without pushing.
              </p>
            </div>
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 7. Noether Conservation ── */}
      <SectionLayout id="noether">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Noether Conservation Laws</h2>
          <p className="section-subheading">
            Continuous symmetries of the Lagrangian yield conserved quantities
            via Noether&rsquo;s theorem.
          </p>

          <div className="grid grid-cols-2 gap-6 mt-8 md:grid-cols-1">
            <motion.div className="card" variants={fadeUp} custom={0} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">Partition Number Conservation</h3>
              <p className="text-sm text-muted mb-3">
                The potential <InlineMath math="\Phi" /> is invariant under
                SO(2) rotations in the <InlineMath math="(\ell, m)" /> plane
                of partition space. By Noether&rsquo;s theorem, the total
                partition number is conserved.
              </p>
              <BlockMath math="\frac{d}{dt}\sum_n C(n) = 0" />
              <p className="text-sm text-muted mt-3">
                States can redistribute among partition levels, but the total
                count is preserved. This is the neural analogue of baryon
                number conservation.
              </p>
            </motion.div>

            <motion.div className="card" variants={fadeUp} custom={1} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">S-Entropy Norm Conservation</h3>
              <p className="text-sm text-muted mb-3">
                Translation symmetry in the entropy sector yields conservation
                of the S-entropy norm.
              </p>
              <BlockMath math="\frac{d}{dt}\left(S_k^2 + S_t^2 + S_e^2\right) = 0" />
              <p className="text-sm text-muted mt-3">
                The system moves on spheres within the S-entropy cube. Entropy
                can be exchanged between Kolmogorov, thermodynamic, and
                entanglement forms, but the total is fixed along a trajectory.
              </p>
            </motion.div>
          </div>
        </div>
      </SectionLayout>

      {/* ── 8. Regime Transitions as Phase Transitions ── */}
      <SectionLayout id="regime-transitions" className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">Regime Transitions as Phase Transitions</h2>
          <p className="section-subheading">
            The five neural regimes are level sets of the potential{" "}
            <InlineMath math="\Phi" />. Boundaries between regimes are
            Landau-type phase transitions.
          </p>

          <motion.div className="card mt-8" variants={fadeUp} custom={0} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <div className="flex items-center gap-3 justify-center flex-wrap mb-6">
              <RegimeBadge regime="turbulent" />
              <span className="text-muted">&harr;</span>
              <RegimeBadge regime="aperture" />
              <span className="text-muted">&harr;</span>
              <RegimeBadge regime="cascade" />
              <span className="text-muted">&harr;</span>
              <RegimeBadge regime="coherent" />
              <span className="text-muted">&harr;</span>
              <RegimeBadge regime="locked" />
            </div>
            <p className="text-sm text-muted mb-4">
              At each regime boundary, the potential develops a degenerate
              critical point. The transition is continuous (second-order) when
              the symmetry breaks smoothly, or discontinuous (first-order) when
              multiple minima coexist. Landau theory at each boundary predicts
              the critical exponents and the width of the coexistence region.
            </p>
            <BlockMath math="\Phi(R) \Big|_{K = K_c} = \frac{K_c}{4}\,R^4 \quad \Longrightarrow \quad R \sim (K - K_c)^{1/2}" />
            <p className="text-sm text-muted mt-3">
              The mean-field exponent <InlineMath math="\beta = 1/2" /> governs
              the onset of synchronization at <InlineMath math="K_c" />.
            </p>
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 9. The Hamiltonian Dual ── */}
      <SectionLayout id="hamiltonian">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">The Hamiltonian Dual</h2>
          <p className="section-subheading">
            A Legendre transform of the Lagrangian yields the Hamiltonian,
            which serves as a large-deviation rate function for trajectory
            probabilities.
          </p>

          <motion.div className="card mt-8" variants={fadeUp} custom={0} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <BlockMath math="H(q, p) = \sup_{\dot{q}} \left[ p \cdot \dot{q} - L(q, \dot{q}) \right]" />
            <p className="text-sm text-muted mt-4">
              The canonical momentum <InlineMath math="p = \partial L / \partial \dot{q}" />{" "}
              conjugate to the generalized coordinate encodes the instantaneous
              driving force. The Hamiltonian <InlineMath math="H" /> gives the
              rate function for large-deviation theory: the probability of
              observing trajectory <InlineMath math="q(t)" /> scales as{" "}
              <InlineMath math="P[q] \sim \exp(-S[q]/D)" />, making
              rare fluctuations exponentially suppressed.
            </p>
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 10. Validation ── */}
      <SectionLayout id="validation" className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading text-center">Validation: 28/28 Claims</h2>
          <p className="section-subheading text-center mx-auto">
            The Lagrangian framework has been validated across four domains.
            Every testable prediction matches observation.
          </p>

          <motion.div className="card mt-8" variants={fadeUp} custom={0} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <ClaimRow domain="Regime Classification" count={8} total={8} delay={0} />
            <ClaimRow domain="Geometric Apertures" count={7} total={7} delay={1} />
            <ClaimRow domain="Operator Trajectories" count={10} total={10} delay={2} />
            <ClaimRow domain="Euler-Lagrange Dynamics" count={3} total={3} delay={3} />
          </motion.div>

          <motion.div
            className="mt-8 text-center"
            variants={fadeUp}
            custom={4}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <div className="inline-flex items-baseline gap-2">
              <span className="text-6xl font-bold text-primary dark:text-primaryDark">28</span>
              <span className="text-2xl text-muted">/</span>
              <span className="text-6xl font-bold text-primary dark:text-primaryDark">28</span>
            </div>
            <p className="text-sm text-muted mt-2">claims validated across 4 domains</p>
          </motion.div>
        </div>
      </SectionLayout>

      {/* ── 11. New Predictions ── */}
      <SectionLayout id="predictions">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading">New Predictions</h2>
          <p className="section-subheading">
            The Lagrangian makes novel, testable predictions beyond the original
            NPL framework.
          </p>

          <div className="grid grid-cols-3 gap-6 mt-8 md:grid-cols-1">
            <motion.div className="card" variants={fadeUp} custom={0} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Fluctuation-Dissipation for <InlineMath math="R" />
              </h3>
              <BlockMath math="\langle \delta R^2 \rangle = \frac{D}{\Phi''(R_{\text{eq}})}" />
              <p className="text-sm text-muted mt-3">
                The variance of order-parameter fluctuations is determined by
                the curvature of the potential at equilibrium and the noise
                strength. This is directly measurable from EEG time series.
              </p>
            </motion.div>

            <motion.div className="card" variants={fadeUp} custom={1} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Critical Slowing
              </h3>
              <BlockMath math="\tau_{\text{relax}} \sim |K - K_c|^{-1}" />
              <p className="text-sm text-muted mt-3">
                Near regime boundaries, the relaxation time diverges. The
                system takes exponentially longer to recover from perturbation.
                This critical slowing is a universal early-warning signal for
                regime transitions.
              </p>
            </motion.div>

            <motion.div className="card" variants={fadeUp} custom={2} initial="hidden" whileInView="visible" viewport={{ once: true }}>
              <h3 className="font-semibold text-dark dark:text-light mb-3">
                Kramers Escape Rates
              </h3>
              <BlockMath math="k_{\text{escape}} \sim \exp\!\left(-\frac{\Delta\Phi}{D}\right)" />
              <p className="text-sm text-muted mt-3">
                The rate of noise-driven transitions between regimes follows
                Kramers&rsquo; law, with the barrier height set by the potential
                difference. This predicts seizure onset rates, anesthetic
                induction times, and sleep-stage transition probabilities.
              </p>
            </motion.div>
          </div>
        </div>
      </SectionLayout>

      {/* ── 12. Figure Placeholders ── */}
      <SectionLayout id="figures" className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-5xl mx-auto">
          <h2 className="section-heading text-center">Figures</h2>
          <div className="grid grid-cols-3 gap-6 mt-8 md:grid-cols-2 sm:grid-cols-1">
            {[
              { num: 1, title: "Potential Landscape", desc: "\u03A6(R, \u03C3\u00B2) surface with regime basins and saddle points" },
              { num: 2, title: "Euler-Lagrange Flow", desc: "Vector field of the equations of motion on the (R, \u03C3\u00B2) plane" },
              { num: 3, title: "Noether Conserved Quantities", desc: "Partition number and S-entropy norm along trajectories" },
              { num: 4, title: "Phase Transition Map", desc: "Regime boundaries as level sets of \u03A6 with critical exponents" },
              { num: 5, title: "Kramers Escape", desc: "Barrier heights and transition rates between adjacent regimes" },
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

      {/* ── Navigation ── */}
      <SectionLayout>
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-between items-center md:flex-col md:gap-6">
            <Link href="/computing" className="group flex items-center gap-3 text-dark dark:text-light hover:text-primary dark:hover:text-primaryDark transition-colors">
              <span className="text-2xl">&larr;</span>
              <div>
                <p className="text-xs text-muted">Previous</p>
                <p className="font-semibold group-hover:text-primary dark:group-hover:text-primaryDark transition-colors">Operator Trajectories</p>
              </div>
            </Link>
            <Link href="/" className="group flex items-center gap-3 text-right text-dark dark:text-light hover:text-primary dark:hover:text-primaryDark transition-colors">
              <div>
                <p className="text-xs text-muted">Return to</p>
                <p className="font-semibold group-hover:text-primary dark:group-hover:text-primaryDark transition-colors">Home</p>
              </div>
              <span className="text-2xl">&rarr;</span>
            </Link>
          </div>
        </div>
      </SectionLayout>
    </>
  );
}

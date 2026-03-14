import React from "react";
import Head from "next/head";
import Link from "next/link";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";
import SectionLayout from "@/components/SectionLayout";
import RegimeBadge from "@/components/RegimeBadge";

const BrainModel = dynamic(() => import("@/components/BrainModel"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center">
      <div className="w-16 h-16 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
    </div>
  ),
});

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.6 },
  }),
};

const StatCard = ({ number, label, delay }) => (
  <motion.div
    className="text-center"
    variants={fadeUp}
    custom={delay}
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true }}
  >
    <div className="text-4xl font-bold text-primary dark:text-primaryDark md:text-3xl">
      {number}
    </div>
    <div className="text-sm text-muted mt-1">{label}</div>
  </motion.div>
);

const PaperCard = ({ title, subtitle, href, regimes, delay }) => (
  <motion.div
    variants={fadeUp}
    custom={delay}
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true }}
  >
    <Link href={href} className="block card group cursor-pointer">
      <div className="flex gap-2 mb-3 flex-wrap">
        {regimes.map((r) => (
          <RegimeBadge key={r} regime={r} />
        ))}
      </div>
      <h3 className="text-lg font-semibold text-dark dark:text-light mb-2 group-hover:text-primary dark:group-hover:text-primaryDark transition-colors">
        {title}
      </h3>
      <p className="text-sm text-muted">{subtitle}</p>
    </Link>
  </motion.div>
);

export default function Home() {
  return (
    <>
      <Head>
        <title>Neural Partition Language | A Variational Framework for Consciousness</title>
      </Head>

      {/* Hero */}
      <section className="relative min-h-[90vh] flex items-center overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern dark:bg-grid-pattern-dark bg-grid opacity-50" />

        <div className="relative z-10 w-full px-32 xl:px-24 lg:px-16 md:px-12 sm:px-8 flex items-center lg:flex-col-reverse lg:py-16">
          <div className="w-1/2 lg:w-full lg:text-center">
            <motion.p
              className="text-sm font-semibold text-primary dark:text-primaryDark uppercase tracking-widest mb-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              Neural Partition Language
            </motion.p>
            <motion.h1
              className="text-5xl font-bold text-dark dark:text-light leading-tight mb-6 xl:text-4xl md:text-3xl sm:text-2xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              One Equation for{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
                All Neural Regimes
              </span>
            </motion.h1>
            <motion.p
              className="text-lg text-muted max-w-xl mb-8 lg:mx-auto md:text-base"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              A unified variational principle derived from three thermodynamic axioms.
              From sleep architecture to drug action, from enzyme catalysis to consciousness
              &mdash; all emerge as necessary consequences of a single Lagrangian.
            </motion.p>
            <motion.div
              className="flex gap-4 lg:justify-center sm:flex-col sm:items-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Link
                href="/framework"
                className="px-8 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors shadow-glow"
              >
                Explore the Framework
              </Link>
              <Link
                href="/validation"
                className="px-8 py-3 border border-dark/10 dark:border-light/10 text-dark dark:text-light rounded-lg font-medium hover:border-primary/30 transition-colors"
              >
                View Results
              </Link>
            </motion.div>
          </div>

          <div className="w-1/2 lg:w-full h-[500px] lg:h-[350px] md:h-[280px]">
            <BrainModel />
          </div>
        </div>
      </section>

      {/* Stats */}
      <SectionLayout className="!py-12 border-y border-dark/5 dark:border-light/5">
        <div className="flex justify-around items-center md:flex-wrap md:gap-8">
          <StatCard number="28/28" label="Validated Claims" delay={0} />
          <StatCard number="5" label="Operational Regimes" delay={1} />
          <StatCard number="11" label="Drugs Modeled" delay={2} />
          <StatCard number="12" label="Enzymes Validated" delay={3} />
          <StatCard number="1" label="Lagrangian" delay={4} />
        </div>
      </SectionLayout>

      {/* Core Insight */}
      <SectionLayout>
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="section-heading">The Core Insight</h2>
          <p className="section-subheading mx-auto">
            If phase space is bounded, null states are forbidden, and observation has finite resolution,
            then neural dynamics are fully determined by a single potential function.
          </p>
          <div className="grid grid-cols-3 gap-6 mt-12 md:grid-cols-1">
            {[
              { axiom: "I", title: "Bounded Phase Space", desc: "The state space has finite measure: \u03BC(\u03A9) < \u221E", color: "from-regime-turbulent to-regime-aperture" },
              { axiom: "II", title: "No Null State", desc: "The system is never in a state of zero activity", color: "from-regime-cascade to-regime-coherent" },
              { axiom: "III", title: "Finite Resolution", desc: "Observational precision is bounded: \u03B4 > 0", color: "from-regime-coherent to-regime-locked" },
            ].map((item, i) => (
              <motion.div key={item.axiom} className="card text-left" variants={fadeUp} custom={i} initial="hidden" whileInView="visible" viewport={{ once: true }}>
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${item.color} flex items-center justify-center text-white font-bold text-sm mb-4`}>
                  {item.axiom}
                </div>
                <h3 className="font-semibold text-dark dark:text-light mb-2">{item.title}</h3>
                <p className="text-sm text-muted">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </SectionLayout>

      {/* Five Regimes */}
      <SectionLayout className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-5xl mx-auto">
          <h2 className="section-heading text-center">Five Operational Regimes</h2>
          <p className="section-subheading text-center mx-auto">
            Every neural state maps to one of five regimes, classified by the Kuramoto order parameter R.
          </p>
          <div className="grid grid-cols-5 gap-4 mt-12 md:grid-cols-2 sm:grid-cols-1">
            {[
              { name: "Turbulent", regime: "turbulent", range: "R < 0.3", desc: "Desynchronized, pathological states" },
              { name: "Aperture", regime: "aperture", range: "0.3 \u2264 R < 0.5", desc: "Selective gating begins" },
              { name: "Cascade", regime: "cascade", range: "0.5 \u2264 R < 0.8", desc: "Cooperative synchronization" },
              { name: "Coherent", regime: "coherent", range: "0.8 \u2264 R < 0.95", desc: "Healthy baseline operation" },
              { name: "Phase-Locked", regime: "locked", range: "R \u2265 0.95", desc: "Hypersynchrony (seizure)" },
            ].map((item, i) => (
              <motion.div key={item.name} className="card text-center !p-6" variants={fadeUp} custom={i} initial="hidden" whileInView="visible" viewport={{ once: true }}>
                <RegimeBadge regime={item.regime} className="mb-3" />
                <div className="text-xs text-muted font-mono mt-2">{item.range}</div>
                <p className="text-xs text-muted mt-2">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </SectionLayout>

      {/* Deep Dives */}
      <SectionLayout>
        <div className="max-w-5xl mx-auto">
          <h2 className="section-heading text-center">Deep Dives</h2>
          <p className="section-subheading text-center mx-auto">
            Each aspect of the framework is developed in detail with full derivations, validation data, and interactive visualizations.
          </p>
          <div className="grid grid-cols-2 gap-6 mt-12 md:grid-cols-1">
            <PaperCard title="Operational Regime Classification" subtitle="From thermodynamic axioms to sleep architecture. Kuramoto synchronization, five regimes, and EEG validation across 500 epochs." href="/regimes" regimes={["turbulent", "cascade", "coherent"]} delay={0} />
            <PaperCard title="Geometric Apertures" subtitle="Zero-work selectivity from categorical constraints. Monopole/dipole/quadrupole taxonomy across 11 antidepressants and 12 enzymes." href="/apertures" regimes={["aperture", "cascade"]} delay={1} />
            <PaperCard title="Operator Trajectories" subtitle="A formal language for bounded phase-space computing. Partition coordinates, S-entropy space, and the pNPL type system." href="/computing" regimes={["coherent", "locked"]} delay={2} />
            <PaperCard title="The Neural Partition Lagrangian" subtitle="One equation for all regimes. Onsager-Machlup action, Noether conservation laws, and 28 validated predictions." href="/lagrangian" regimes={["turbulent", "aperture", "cascade", "coherent", "locked"]} delay={3} />
          </div>
        </div>
      </SectionLayout>

      {/* CTA */}
      <SectionLayout className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="section-heading">Collaborate With Us</h2>
          <p className="section-subheading mx-auto">
            We are looking for collaborators and partners to validate, extend, and apply this framework
            to clinical neuroscience, drug discovery, and neural computing.
          </p>
          <div className="flex gap-4 justify-center sm:flex-col sm:items-center">
            <Link href="/about" className="px-8 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors">
              Get in Touch
            </Link>
            <Link href="/framework" className="px-8 py-3 border border-dark/10 dark:border-light/10 text-dark dark:text-light rounded-lg font-medium hover:border-primary/30 transition-colors">
              Read the Theory
            </Link>
          </div>
        </div>
      </SectionLayout>
    </>
  );
}

import React from "react";
import Head from "next/head";
import Link from "next/link";
import { motion } from "framer-motion";
import SectionLayout from "@/components/SectionLayout";

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.6 },
  }),
};

const ApplicationCard = ({ title, icon, description, delay }) => (
  <motion.div
    className="card"
    variants={fadeUp}
    custom={delay}
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true }}
  >
    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-2xl mb-4">
      {icon}
    </div>
    <h3 className="text-lg font-semibold text-dark dark:text-light mb-2">
      {title}
    </h3>
    <p className="text-sm text-muted">{description}</p>
  </motion.div>
);

export default function About() {
  return (
    <>
      <Head>
        <title>About | Neural Partition Language</title>
        <meta
          name="description"
          content="About the Neural Partition Language framework and its creator Kundai Farai Sachikonye. A unified mathematical theory of consciousness grounded in thermodynamics."
        />
      </Head>

      {/* Hero */}
      <section className="relative min-h-[50vh] flex items-center overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern dark:bg-grid-pattern-dark bg-grid opacity-50" />
        <div className="relative z-10 w-full px-32 xl:px-24 lg:px-16 md:px-12 sm:px-8 py-16">
          <div className="max-w-4xl mx-auto text-center">
            <motion.h1
              className="text-5xl font-bold text-dark dark:text-light leading-tight mb-6 xl:text-4xl md:text-3xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              About the{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
                Framework
              </span>
            </motion.h1>
            <motion.p
              className="text-lg text-muted max-w-2xl mx-auto md:text-base"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              A first-principles approach to understanding neural dynamics,
              built at the intersection of thermodynamics, information theory,
              and mathematical physics.
            </motion.p>
          </div>
        </div>
      </section>

      {/* Researcher */}
      <SectionLayout>
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-3 gap-12 items-start md:grid-cols-1">
            <motion.div
              className="col-span-1"
              variants={fadeUp}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              <div className="w-full aspect-square rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 border border-primary/10 flex items-center justify-center">
                <div className="text-center p-6">
                  <div className="text-6xl font-bold text-primary dark:text-primaryDark mb-2">
                    KS
                  </div>
                  <div className="text-xs text-muted uppercase tracking-widest">
                    Researcher
                  </div>
                </div>
              </div>
            </motion.div>

            <motion.div
              className="col-span-2 md:col-span-1"
              variants={fadeUp}
              custom={1}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              <h2 className="text-3xl font-bold text-dark dark:text-light mb-1">
                Kundai Farai Sachikonye
              </h2>
              <p className="text-sm text-primary dark:text-primaryDark font-medium mb-4">
                AIMe Registry for Artificial Intelligence
              </p>
              <p className="text-muted mb-4">
                <a
                  href="mailto:kundai.sachikonye@bitspark.com"
                  className="text-primary dark:text-primaryDark hover:underline"
                >
                  kundai.sachikonye@bitspark.com
                </a>
              </p>
            </motion.div>
          </div>
        </div>
      </SectionLayout>

      {/* Vision */}
      <SectionLayout className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-4xl mx-auto">
          <h2 className="section-heading text-center">Vision</h2>
          <motion.div
            className="max-w-3xl mx-auto"
            variants={fadeUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <p className="text-lg text-muted text-center leading-relaxed">
              The goal of this work is to establish a complete, self-consistent
              mathematical framework for consciousness &mdash; one grounded not in
              metaphor or analogy, but in the same thermodynamic principles that
              govern every other physical system. From three axioms, we derive
              partition coordinates, entropy geometry, five operational regimes,
              and a single Lagrangian whose Euler-Lagrange equations reproduce
              known neural dynamics. Every prediction is testable. Every claim has
              been validated against experimental data.
            </p>
          </motion.div>
        </div>
      </SectionLayout>

      {/* Applications */}
      <SectionLayout>
        <div className="max-w-5xl mx-auto">
          <h2 className="section-heading text-center">Applications</h2>
          <p className="section-subheading text-center mx-auto">
            The partition framework opens concrete pathways across medicine,
            pharmacology, computing, and neurotechnology.
          </p>
          <div className="grid grid-cols-2 gap-6 mt-12 md:grid-cols-1">
            <ApplicationCard
              title="Clinical Neuroscience"
              icon={
                <svg
                  className="w-6 h-6 text-primary dark:text-primaryDark"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"
                  />
                </svg>
              }
              description="Objective sleep disorder diagnosis via regime classification of EEG data. Real-time consciousness monitoring during anaesthesia using the structural factor S(R, sigma-squared). Seizure prediction through phase-locked regime early warning."
              delay={0}
            />
            <ApplicationCard
              title="Drug Discovery"
              icon={
                <svg
                  className="w-6 h-6 text-primary dark:text-primaryDark"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5"
                  />
                </svg>
              }
              description="Rational antidepressant design using the geometric aperture taxonomy. Monopole, dipole, and quadrupole selectivity profiles predict drug action from molecular structure, enabling targeted pharmacological intervention."
              delay={1}
            />
            <ApplicationCard
              title="Neural Computing"
              icon={
                <svg
                  className="w-6 h-6 text-primary dark:text-primaryDark"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25z"
                  />
                </svg>
              }
              description="Partition coordinates define a novel computing substrate. Poincare computing exploits recurrence structure for efficient computation. Backward determination enables inference of initial conditions from observed trajectories."
              delay={2}
            />
            <ApplicationCard
              title="Brain-Computer Interfaces"
              icon={
                <svg
                  className="w-6 h-6 text-primary dark:text-primaryDark"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5"
                  />
                </svg>
              }
              description="Real-time regime classification from streaming EEG provides a principled decoding layer for brain-computer interfaces. The five-regime taxonomy offers a natural vocabulary for neural state communication."
              delay={3}
            />
          </div>
        </div>
      </SectionLayout>

      {/* Collaboration */}
      <SectionLayout className="bg-dark/[0.02] dark:bg-light/[0.02]">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="section-heading">Collaborate With Us</h2>
          <motion.div
            variants={fadeUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <p className="text-lg text-muted mb-4 leading-relaxed">
              The Neural Partition Language framework is at an inflection point.
              The theoretical foundation is complete and validated against
              experimental data across sleep, pharmacology, and enzymology. The
              next phase &mdash; clinical translation, computational tooling, and
              large-scale validation &mdash; requires collaboration.
            </p>
            <p className="text-muted mb-8">
              We welcome engagement from researchers in neuroscience, physics,
              and mathematics; clinicians with access to EEG/MEG datasets;
              pharmaceutical scientists exploring rational drug design; and
              investors who see the potential of a first-principles approach to
              brain science.
            </p>
          </motion.div>
        </div>
      </SectionLayout>

      {/* Contact */}
      <SectionLayout>
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="section-heading">Get in Touch</h2>
          <motion.div
            variants={fadeUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <p className="text-muted mb-6">
              For research collaboration, investment enquiries, or general
              questions about the framework.
            </p>
            <a
              href="mailto:kundai.sachikonye@bitspark.com"
              className="inline-block px-8 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors shadow-glow"
            >
              kundai.sachikonye@bitspark.com
            </a>
          </motion.div>
        </div>
      </SectionLayout>
    </>
  );
}

import React from "react";
import { motion } from "framer-motion";

const SectionLayout = ({ children, className = "", id = "" }) => {
  return (
    <motion.section
      id={id}
      className={`w-full px-32 py-16 xl:px-24 lg:px-16 md:px-12 sm:px-8 ${className}`}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      viewport={{ once: true, margin: "-100px" }}
    >
      {children}
    </motion.section>
  );
};

export default SectionLayout;

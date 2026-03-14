import Link from "next/link";
import React from "react";
import Layout from "./Layout";

const Footer = () => {
  return (
    <footer className="w-full border-t border-dark/5 dark:border-light/5 font-medium text-sm dark:text-light/60 text-dark/60">
      <Layout className="!py-8 flex items-center justify-between lg:flex-col lg:gap-4">
        <span>{new Date().getFullYear()} Kundai Sachikonye. All Rights Reserved.</span>
        <div className="flex items-center gap-6">
          <Link href="/framework" className="hover:text-primary dark:hover:text-primaryDark transition-colors">
            Framework
          </Link>
          <Link href="/validation" className="hover:text-primary dark:hover:text-primaryDark transition-colors">
            Validation
          </Link>
          <Link href="/about" className="hover:text-primary dark:hover:text-primaryDark transition-colors">
            Contact
          </Link>
        </div>
        <span className="text-xs text-muted">Neural Partition Language</span>
      </Layout>
    </footer>
  );
};

export default Footer;

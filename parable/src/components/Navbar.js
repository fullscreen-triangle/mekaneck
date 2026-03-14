import Link from "next/link";
import React, { useState } from "react";
import Logo from "./Logo";
import { useRouter } from "next/router";
import { GithubIcon, LinkedInIcon } from "./Icons";
import { motion } from "framer-motion";
import { useThemeSwitch } from "./Hooks/useThemeSwitch";

const CustomLink = ({ href, title, className = "" }) => {
  const router = useRouter();
  const isActive = router.asPath === href;

  return (
    <Link
      href={href}
      className={`${className} relative text-sm font-medium transition-colors duration-200
        ${isActive ? "text-primaryDark" : "text-light/70 hover:text-light"}`}
    >
      {title}
      {isActive && (
        <motion.span
          layoutId="navbar-indicator"
          className="absolute -bottom-1 left-0 w-full h-0.5 bg-primaryDark rounded-full"
        />
      )}
    </Link>
  );
};

const CustomMobileLink = ({ href, title, className = "", toggle }) => {
  const router = useRouter();
  const isActive = router.asPath === href;

  const handleClick = () => {
    toggle();
    router.push(href);
  };

  return (
    <button
      className={`${className} text-base font-medium transition-colors duration-200
        ${isActive ? "text-primaryDark" : "text-light/80"}`}
      onClick={handleClick}
    >
      {title}
    </button>
  );
};

const Navbar = () => {
  useThemeSwitch();
  const [isOpen, setIsOpen] = useState(false);

  const handleClick = () => {
    setIsOpen(!isOpen);
  };

  return (
    <header
      className="w-full flex items-center justify-between px-32 py-6 font-medium z-10 text-light
      lg:px-16 relative md:px-12 sm:px-8 border-b border-light/5 bg-dark/80 backdrop-blur-md"
    >
      {/* Mobile hamburger */}
      <button
        type="button"
        className="flex-col items-center justify-center hidden lg:flex"
        aria-controls="mobile-menu"
        aria-expanded={isOpen}
        onClick={handleClick}
      >
        <span className="sr-only">Open main menu</span>
        <span
          className={`bg-light block h-0.5 w-6 rounded-sm transition-all duration-300 ease-out ${
            isOpen ? "rotate-45 translate-y-1" : "-translate-y-0.5"
          }`}
        />
        <span
          className={`bg-light block h-0.5 w-6 rounded-sm transition-all duration-300 ease-out ${
            isOpen ? "opacity-0" : "opacity-100"
          } my-0.5`}
        />
        <span
          className={`bg-light block h-0.5 w-6 rounded-sm transition-all duration-300 ease-out ${
            isOpen ? "-rotate-45 -translate-y-1" : "translate-y-0.5"
          }`}
        />
      </button>

      {/* Desktop nav */}
      <div className="w-full flex justify-between items-center lg:hidden">
        <nav className="flex items-center gap-6">
          <CustomLink href="/" title="Home" />
          <CustomLink href="/framework" title="Framework" />
          <CustomLink href="/regimes" title="Regimes" />
          <CustomLink href="/apertures" title="Apertures" />
          <CustomLink href="/computing" title="Computing" />
          <CustomLink href="/lagrangian" title="Lagrangian" />
          <CustomLink href="/validation" title="Validation" />
          <CustomLink href="/about" title="About" />
        </nav>

        <nav className="flex items-center gap-3">
          <motion.a
            target="_blank"
            className="w-5 opacity-60 hover:opacity-100 transition-opacity"
            href="https://github.com"
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.9 }}
            aria-label="GitHub"
          >
            <GithubIcon />
          </motion.a>
          <motion.a
            target="_blank"
            className="w-5 opacity-60 hover:opacity-100 transition-opacity"
            href="https://linkedin.com"
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.9 }}
            aria-label="LinkedIn"
          >
            <LinkedInIcon />
          </motion.a>
        </nav>
      </div>

      {/* Mobile nav */}
      {isOpen ? (
        <motion.div
          className="min-w-[70vw] sm:min-w-[90vw] flex items-center flex-col fixed top-1/2 left-1/2 -translate-x-1/2
          -translate-y-1/2 py-16 bg-dark/95 rounded-2xl z-50 backdrop-blur-md"
          initial={{ scale: 0, x: "-50%", y: "-50%", opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
        >
          <nav className="flex items-center justify-center flex-col gap-4">
            <CustomMobileLink toggle={handleClick} href="/" title="Home" />
            <CustomMobileLink toggle={handleClick} href="/framework" title="Framework" />
            <CustomMobileLink toggle={handleClick} href="/regimes" title="Regimes" />
            <CustomMobileLink toggle={handleClick} href="/apertures" title="Apertures" />
            <CustomMobileLink toggle={handleClick} href="/computing" title="Computing" />
            <CustomMobileLink toggle={handleClick} href="/lagrangian" title="Lagrangian" />
            <CustomMobileLink toggle={handleClick} href="/validation" title="Validation" />
            <CustomMobileLink toggle={handleClick} href="/about" title="About" />
          </nav>
        </motion.div>
      ) : null}

      <div className="absolute left-[50%] top-2 translate-x-[-50%] lg:hidden">
        <Logo />
      </div>
    </header>
  );
};

export default Navbar;

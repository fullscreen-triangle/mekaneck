import React from "react";

const regimeStyles = {
  turbulent: "bg-regime-turbulent/10 text-regime-turbulent border border-regime-turbulent/20",
  aperture: "bg-regime-aperture/10 text-regime-aperture border border-regime-aperture/20",
  cascade: "bg-regime-cascade/10 text-regime-cascade border border-regime-cascade/20",
  coherent: "bg-regime-coherent/10 text-regime-coherent border border-regime-coherent/20",
  locked: "bg-regime-locked/10 text-regime-locked border border-regime-locked/20",
};

const RegimeBadge = ({ regime, className = "" }) => {
  return (
    <span className={`regime-badge ${regimeStyles[regime] || ""} ${className}`}>
      {regime === "locked" ? "Phase-Locked" : regime}
    </span>
  );
};

export default RegimeBadge;

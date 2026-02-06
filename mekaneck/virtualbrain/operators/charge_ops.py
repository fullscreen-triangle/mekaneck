"""
Charge Operators: CONSERVE, REDISTRIBUTE.

Implements charge conservation and redistribution operations
for the charge-naming circuit isomorphism.

The soul (charge distribution) and consciousness (naming system)
are isomorphic structures operating on the same physical substrate.
"""

from typing import Tuple, Optional
import numpy as np


def CONSERVE(rho: np.ndarray) -> float:
    """
    CONSERVE operator: Compute total charge (verify conservation).

    integral(rho, V) = Q_total = const

    The total charge is conserved in the non-grounded circuit.

    Args:
        rho: Charge density array

    Returns:
        Total charge
    """
    return float(np.sum(rho))


def REDISTRIBUTE(
    rho: np.ndarray,
    target: np.ndarray,
    rate: float = 0.1,
) -> np.ndarray:
    """
    REDISTRIBUTE operator: Redistribute charge toward target.

    Moves charge to minimize variance while conserving total charge.

    Args:
        rho: Current charge distribution
        target: Target charge distribution
        rate: Redistribution rate

    Returns:
        Updated charge distribution (conserves total)
    """
    # Compute difference
    diff = target - rho

    # Apply rate-limited redistribution
    delta = rate * diff

    # Ensure conservation by removing mean
    delta = delta - np.mean(delta)

    return rho + delta


def charge_variance(rho: np.ndarray) -> float:
    """
    Compute charge variance.

    sigma^2 = <(rho - <rho>)^2>

    Lower variance indicates more uniform distribution.

    Args:
        rho: Charge density array

    Returns:
        Variance of charge distribution
    """
    return float(np.var(rho))


def minimize_variance(
    rho: np.ndarray,
    max_iterations: int = 100,
    tolerance: float = 1e-6,
) -> Tuple[np.ndarray, float]:
    """
    Redistribute charge to minimize variance.

    Variance minimization drives charge redistribution toward
    uniform distribution (equilibrium).

    Args:
        rho: Initial charge distribution
        max_iterations: Maximum iterations
        tolerance: Convergence tolerance

    Returns:
        (final_distribution, final_variance)
    """
    current = rho.copy()
    target = np.full_like(rho, np.mean(rho))

    for _ in range(max_iterations):
        var = charge_variance(current)
        if var < tolerance:
            break

        current = REDISTRIBUTE(current, target, rate=0.1)

    return current, charge_variance(current)


def charge_continuity(
    rho: np.ndarray,
    J: np.ndarray,
    dt: float,
    dx: float = 1.0,
) -> np.ndarray:
    """
    Apply charge continuity equation.

    d(rho)/dt + div(J) = 0

    Args:
        rho: Current charge density
        J: Current density (flux)
        dt: Time step
        dx: Spatial step

    Returns:
        Updated charge density
    """
    # Compute divergence of J (1D case)
    div_J = np.gradient(J, dx)

    # Update rho
    rho_new = rho - div_J * dt

    return rho_new


def couple_charge_consciousness(
    rho: np.ndarray,
    consciousness: float,
    coupling: float = 0.1,
) -> np.ndarray:
    """
    Couple charge distribution to consciousness level.

    The charge-naming isomorphism means consciousness modulates
    charge redistribution dynamics.

    Args:
        rho: Charge distribution
        consciousness: Consciousness level in [0, 1]
        coupling: Coupling strength

    Returns:
        Modulated charge distribution
    """
    # Higher consciousness -> faster equilibration
    rate = coupling * consciousness

    # Target is uniform distribution
    target = np.full_like(rho, np.mean(rho))

    return REDISTRIBUTE(rho, target, rate=rate)


def charge_equilibrium(
    rho: np.ndarray,
    temperature: float = 300.0,
) -> np.ndarray:
    """
    Compute thermal equilibrium charge distribution.

    Uses Boltzmann distribution for equilibrium.

    Args:
        rho: Current charge distribution
        temperature: Temperature in Kelvin

    Returns:
        Equilibrium distribution
    """
    from ..core.constants import BOLTZMANN_CONSTANT

    kT = BOLTZMANN_CONSTANT * temperature

    # Assume energy proportional to charge imbalance
    mean_rho = np.mean(rho)
    energy = (rho - mean_rho) ** 2

    # Boltzmann weights
    weights = np.exp(-energy / kT)
    weights = weights / np.sum(weights)

    # Equilibrium distribution
    total_charge = np.sum(rho)
    return weights * total_charge


def surface_coupling(
    rho_electric: np.ndarray,
    c_chemical: np.ndarray,
    coupling_constant: float = 1.0,
) -> float:
    """
    COUPLE_SC operator: Compute surface coupling potential.

    Couples electrical charge distribution to chemical concentration.

    Args:
        rho_electric: Electric charge density
        c_chemical: Chemical concentration
        coupling_constant: Coupling strength

    Returns:
        Surface coupling potential Phi
    """
    # Cross-correlation gives coupling strength
    Phi = coupling_constant * np.sum(rho_electric * c_chemical)
    return float(Phi)

//! Conformance against `chatelier/validation/validate_policy.py`.
//!
//! Two of these encode *counterexamples* rather than confirmations. The
//! optimality claim for the threshold rule holds only for divisible
//! repertoires, and a cycle basis certifies only exact coherence — both
//! boundaries were found by the validation and are pinned here so a later
//! change cannot quietly widen the claim.

use mekaneck_policy::*;

fn cand(id: &str, cost: f64, gain: f64) -> Candidate {
    Candidate::new(id, cost, gain).unwrap()
}

/// Brute-force 0/1 knapsack, for checking the greedy rule against truth.
fn optimum(cands: &[Candidate], budget: f64) -> f64 {
    let n = cands.len();
    let mut best = 0.0f64;
    for mask in 0u32..(1 << n) {
        let mut c = 0.0;
        let mut g = 0.0;
        for (i, cd) in cands.iter().enumerate() {
            if mask & (1 << i) != 0 {
                c += cd.cost;
                g += cd.gain;
            }
        }
        if c <= budget + 1e-12 && g > best {
            best = g;
        }
    }
    best
}

/// Thm 8.2(ii): exact optimality on a divisible repertoire.
///
/// Python: 0 suboptimal cases in 400 trials with unit-cost responses.
#[test]
fn divisible_repertoire_is_exactly_optimal() {
    let mut seed = 0x51ed_270b_u64;
    let mut next = || {
        seed ^= seed << 13;
        seed ^= seed >> 7;
        seed ^= seed << 17;
        (seed >> 11) as f64 / (1u64 << 53) as f64
    };

    for _ in 0..300 {
        let n = 4 + (next() * 6.0) as usize;
        let cands: Vec<Candidate> = (0..n)
            .map(|i| cand(&format!("c{i}"), 0.25, 0.25 * (0.4 + next())))
            .collect();
        assert!(is_divisible(&cands));

        let budget_units = 2 + (next() * 6.0) as usize;
        let budget = 0.25 * budget_units as f64;
        let s = select(&cands, Budget::new(budget, 0.25).unwrap());
        let opt = optimum(&cands, budget);

        assert!(
            s.total_gain >= opt - 1e-9,
            "greedy {} below optimum {} on a divisible repertoire",
            s.total_gain,
            opt
        );
    }
}

/// Rem 8.3: the exact claim FAILS on indivisible bundles, even when every
/// cost is a multiple of the floor.
///
/// This is the witness the validation produced. It is pinned as a test so the
/// boundary of clause (ii) cannot be widened by accident.
#[test]
fn indivisible_bundles_defeat_exact_optimality() {
    // costs (0.5, 0.5, 0.75, 0.5, 0.75, 1.0), gains (0.2, 0.2, 0.3, 0.4, 0.6, 0.8)
    // budget 1.75: greedy attains 1.2, the optimum is 1.4.
    let cands = vec![
        cand("a", 0.5, 0.2),
        cand("b", 0.5, 0.2),
        cand("c", 0.75, 0.3),
        cand("d", 0.5, 0.4),
        cand("e", 0.75, 0.6),
        cand("f", 1.0, 0.8),
    ];
    // every cost is a multiple of the floor...
    for c in &cands {
        assert!((c.cost / 0.25).fract().abs() < 1e-12);
    }
    // ...but the repertoire is not divisible
    assert!(!is_divisible(&cands));

    let budget = 1.75;
    let s = select(&cands, Budget::new(budget, 0.25).unwrap());
    let opt = optimum(&cands, budget);

    assert!((s.total_gain - 1.2).abs() < 1e-9, "greedy {}", s.total_gain);
    assert!((opt - 1.4).abs() < 1e-9, "optimum {opt}");
    assert!(s.total_gain < opt, "the gap is the point of this test");

    // The gap is bounded by a single candidate's gain (clause (i) survives).
    let largest = cands.iter().fold(0.0f64, |a, c| a.max(c.gain));
    assert!(opt - s.total_gain <= largest + 1e-9);
}

/// Prop 8.4: the shadow price is non-increasing in the budget.
///
/// Python: 0 non-monotone cases in 300 trials, using the first-excluded
/// definition. The last-admitted definition is non-monotone and is not used.
#[test]
fn shadow_price_falls_as_the_budget_widens() {
    let cands = vec![
        cand("a", 1.0, 1.0),
        cand("b", 0.5, 0.45),
        cand("c", 2.0, 1.6),
        cand("d", 0.75, 0.5),
        cand("e", 1.5, 0.9),
    ];

    let mut prev = f64::INFINITY;
    for steps in 1..=20 {
        let budget = 0.5 * steps as f64;
        let s = select(&cands, Budget::new(budget, 0.25).unwrap());
        let price = s.shadow_price.unwrap_or(0.0);
        assert!(
            price <= prev + 1e-12,
            "price rose from {prev} to {price} as the budget widened to {budget}"
        );
        prev = price;
    }
    // and it reaches zero once nothing is excluded
    let wide = select(&cands, Budget::new(100.0, 0.25).unwrap());
    assert!(wide.shadow_price.is_none());
    assert!(!wide.declined_any());
}

/// Cor 8.4: declining is forced by boundedness alone.
#[test]
fn declining_is_forced_not_chosen() {
    let b = Budget::new(1.0, 0.25).unwrap();
    assert_eq!(b.max_commitments(), 4);

    // ten candidates of identical, maximal gain: four is all the budget buys
    let cands: Vec<Candidate> = (0..10)
        .map(|i| cand(&format!("c{i}"), 0.25, 1.0))
        .collect();
    let s = select(&cands, b);
    assert_eq!(s.committed.len(), 4);
    assert_eq!(s.declined.len(), 6);
}

/// Cor 4.x: relay drift is the composition law.
///
/// Python: max deviation 2.22e-16 over 1200 chains of length 1 to 25.
#[test]
fn relay_drift_is_composition() {
    use mekaneck_algebra::{compose, Power};

    for ks in [
        vec![0.2],
        vec![0.2, 0.3],
        vec![0.2, 0.35, 0.1, 0.4],
        vec![-0.1, 0.5, 0.25],
        vec![0.05; 25],
    ] {
        let powers: Vec<Power> = ks.iter().map(|k| Power::new(*k).unwrap()).collect();
        let mut relayed = Relayed::origin(());
        for p in &powers {
            relayed = relayed.relay(*p);
        }
        let composed = compose(&powers).unwrap();
        assert!(
            (relayed.drift() - composed.kappa()).abs() < 1e-12,
            "chain of {} relays: drift {} vs composed {}",
            ks.len(),
            relayed.drift(),
            composed.kappa()
        );
        assert_eq!(relayed.depth, ks.len());
    }
}

/// Fidelity decays geometrically when relay powers are bounded below.
///
/// Python: fidelity after 10 relays at k = 0.2 is 0.1074.
#[test]
fn fidelity_decays_geometrically() {
    let bound = fidelity_bound(10, 0.2).unwrap();
    assert!((bound - 0.107_374_182_4).abs() < 1e-9, "bound {bound}");

    // relays needed to halve fidelity at k = 0.2
    assert_eq!(relays_until(0.5, 0.2), Some(4));
}

/// Prop 9.2: phase exclusion caps commitment independently of the budget.
#[test]
fn phase_exclusion_caps_throughput() {
    use Phase::*;

    // a quarter of instants spent constructing
    let mut log = PhaseLog::new();
    for i in 0..100 {
        log.record(if i % 4 == 0 { Constructing } else { Committing });
    }
    assert!((log.construction_fraction() - 0.25).abs() < 1e-12);
    assert_eq!(log.permitted_commitments(100), 75);

    // The ceiling is independent of the budget: no budget raises it.
    let generous = Budget::new(1e6, 0.25).unwrap();
    assert!(generous.max_commitments() > 1000);
    assert_eq!(log.permitted_commitments(100), 75);
}

/// Rem 9.3: the two ceilings are reported separately.
#[test]
fn budget_and_phase_bounds_are_distinguished() {
    use Phase::*;

    let no_construction = {
        let mut l = PhaseLog::new();
        l.record(Committing);
        l
    };
    let with_construction = {
        let mut l = PhaseLog::new();
        l.record(Constructing);
        l.record(Committing);
        l
    };

    assert_eq!(classify_quiescence(0, &no_construction), Quiescence::Exhausted);
    assert_eq!(classify_quiescence(5, &no_construction), Quiescence::BudgetBound);
    assert_eq!(classify_quiescence(0, &with_construction), Quiescence::PhaseBound);
    assert_eq!(classify_quiescence(5, &with_construction), Quiescence::Both);
}

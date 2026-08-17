//! Type checker (Paper 3, §5).
//!
//! Five types and two non-standard rules:
//!
//! - **T-Seek-Pos** (Def 5.3): a `seek` is well typed only if the substrate's
//!   floor is strictly positive. A program may not assert an attainable zero
//!   residual.
//! - **T-Seek-Coh** (Def 5.4): a `via` clause must name at least three
//!   *mutually* declared-independent catalysts. Thm 6.2 shows no acyclic
//!   support structure is robust and that 1- and 2-cycles fail, so three is
//!   the minimum, not a heuristic.
//!
//! What the checker cannot do is verify the independence it requires
//! (Rem 6.3). It requires the claim to be written down and auditable.

use std::collections::{BTreeMap, BTreeSet};

use serde::{Deserialize, Serialize};

use crate::ast::*;
use crate::lex::Span;
use crate::Error;

/// The five types of Def 5.1. There is deliberately no `Point`: the language
/// cannot express a residue-free answer (Rem 3.4).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Ty {
    Substrate,
    Catalyst,
    Cell,
    Outcome,
    Floor,
}

/// Minimum catalysts for a robust support structure (Thm 6.2).
pub const MIN_COHERENCE: usize = 3;

/// Floor values supplied by the substrate bindings, keyed by substrate name.
///
/// The checker cannot compute these — they come from data — so they are an
/// input. A substrate whose floor is absent is checked for everything except
/// T-Seek-Pos, and [`TypeEnv::unchecked_floors`] records which.
pub type FloorValues = BTreeMap<String, f64>;

#[derive(Debug, Clone, Default)]
pub struct TypeEnv {
    pub bindings: BTreeMap<String, Ty>,
    pub catalyst_independence: BTreeMap<String, BTreeSet<String>>,
    /// Substrates whose floor was not supplied, so T-Seek-Pos went unchecked.
    pub unchecked_floors: Vec<String>,
}

/// Type-check a program against the floors its substrates report.
pub fn typecheck(prog: &Program, floors: &FloorValues) -> Result<TypeEnv, Error> {
    let mut env = TypeEnv::default();

    for s in prog.substrates() {
        if env.bindings.contains_key(&s.name) {
            return Err(Error::Duplicate {
                name: s.name.clone(),
                span: s.span,
            });
        }
        env.bindings.insert(s.name.clone(), Ty::Substrate);
    }
    if env.bindings.is_empty() {
        return Err(Error::NoSubstrate);
    }

    for c in prog.catalysts() {
        if env.bindings.contains_key(&c.name) {
            return Err(Error::Duplicate {
                name: c.name.clone(),
                span: c.span,
            });
        }
        env.bindings.insert(c.name.clone(), Ty::Catalyst);
        env.catalyst_independence
            .insert(c.name.clone(), c.independent.iter().cloned().collect());
    }

    // An independence declaration naming an unknown catalyst is an error: the
    // claim it makes is unverifiable in a way the checker *can* detect.
    for c in prog.catalysts() {
        for other in &c.independent {
            if !env.catalyst_independence.contains_key(other) {
                return Err(Error::UnknownCatalyst {
                    name: other.clone(),
                    span: c.span,
                });
            }
            if other == &c.name {
                return Err(Error::SelfIndependence {
                    name: c.name.clone(),
                    span: c.span,
                });
            }
        }
    }

    // T-Seek-Pos, once per substrate: the floor is a property of the binding,
    // not of an individual seek.
    for s in prog.substrates() {
        match floors.get(&s.name) {
            Some(&beta) => {
                if beta.is_nan() || beta <= 0.0 {
                    return Err(Error::NonPositiveFloor {
                        substrate: s.name.clone(),
                        value: beta,
                        span: s.floor.span(),
                    });
                }
            }
            None => env.unchecked_floors.push(s.name.clone()),
        }
    }

    for l in prog.lets() {
        check_seek(&l.seek, &env)?;
        env.bindings.insert(l.name.clone(), Ty::Outcome);
    }

    for r in prog.reports() {
        if !env.bindings.contains_key(&r.name) {
            return Err(Error::Unbound {
                name: r.name.clone(),
                span: r.span,
            });
        }
    }

    Ok(env)
}

fn check_seek(seek: &SeekExpr, env: &TypeEnv) -> Result<(), Error> {
    if seek.via.is_empty() {
        return Ok(()); // no explicit chain: T-Seek-Coh does not apply
    }
    let span = seek.via_span.unwrap_or(seek.span);

    for c in &seek.via {
        if !env.catalyst_independence.contains_key(c) {
            return Err(Error::UnknownCatalyst {
                name: c.clone(),
                span,
            });
        }
    }

    let mut seen = BTreeSet::new();
    for c in &seek.via {
        if !seen.insert(c.clone()) {
            return Err(Error::DuplicateCatalyst {
                name: c.clone(),
                span,
            });
        }
    }

    // T-Seek-Coh, part 1: the count.
    if seek.via.len() < MIN_COHERENCE {
        return Err(Error::InsufficientCoherence {
            got: seek.via.len(),
            need: MIN_COHERENCE,
            span,
        });
    }

    // T-Seek-Coh, part 2: mutual independence. Checking the relation and not
    // merely the count is what distinguishes this from a size heuristic.
    for a in &seek.via {
        for b in &seek.via {
            if a == b {
                continue;
            }
            let indep = env.catalyst_independence.get(a).expect("checked above");
            if !indep.contains(b) {
                return Err(Error::NotMutuallyIndependent {
                    a: a.clone(),
                    b: b.clone(),
                    span,
                });
            }
        }
    }
    Ok(())
}

/// A diagnostic for the editor: a message plus the span it applies to.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Diagnostic {
    pub message: String,
    pub span: Span,
    pub severity: Severity,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Severity {
    Error,
    Warning,
}

/// Check a source string and return diagnostics rather than a single error,
/// which is the shape the editor consumes.
pub fn diagnose(src: &str, floors: &FloorValues) -> Vec<Diagnostic> {
    let prog = match crate::parse::parse(src) {
        Ok(p) => p,
        Err(e) => {
            return vec![Diagnostic {
                message: e.to_string(),
                span: e.span().unwrap_or(Span::new(0, 0)),
                severity: Severity::Error,
            }]
        }
    };
    match typecheck(&prog, floors) {
        Ok(env) => env
            .unchecked_floors
            .iter()
            .filter_map(|name| {
                prog.substrates().find(|s| &s.name == name).map(|s| Diagnostic {
                    message: format!(
                        "floor for substrate {name:?} was not supplied, so T-Seek-Pos is unchecked; \
                         the declared estimator decides whether a positive result could have failed"
                    ),
                    span: s.floor.span(),
                    severity: Severity::Warning,
                })
            })
            .collect(),
        Err(e) => vec![Diagnostic {
            message: e.to_string(),
            span: e.span().unwrap_or(Span::new(0, 0)),
            severity: Severity::Error,
        }],
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parse::parse;

    fn floors(v: f64) -> FloorValues {
        let mut m = FloorValues::new();
        m.insert("Osc".to_string(), v);
        m
    }

    const P: &str = r#"
substrate Osc { receivers : r(); observable : o(); events : e(); floor : asymptotic_separation(); }
catalyst a : f() independent b, c;
catalyst b : g() independent a, c;
catalyst c : h() independent a, b;
let x = seek t() excluding rest() via (a, b, c) until closure;
report x;
"#;

    #[test]
    fn conforming_program_types() {
        assert!(typecheck(&parse(P).unwrap(), &floors(12.5)).is_ok());
    }

    #[test]
    fn zero_and_negative_floors_are_rejected() {
        for v in [0.0, -3.0] {
            assert!(matches!(
                typecheck(&parse(P).unwrap(), &floors(v)),
                Err(Error::NonPositiveFloor { .. })
            ));
        }
    }

    #[test]
    fn two_catalysts_are_rejected() {
        let src = P.replace("via (a, b, c)", "via (a, b)");
        match typecheck(&parse(&src).unwrap(), &floors(5.0)) {
            Err(Error::InsufficientCoherence { got, need, .. }) => {
                assert_eq!((got, need), (2, 3));
            }
            other => panic!("expected InsufficientCoherence, got {other:?}"),
        }
    }

    #[test]
    fn three_catalysts_not_mutually_independent_are_rejected() {
        let src = P.replace("catalyst c : h() independent a, b;", "catalyst c : h();");
        assert!(matches!(
            typecheck(&parse(&src).unwrap(), &floors(5.0)),
            Err(Error::NotMutuallyIndependent { .. })
        ));
    }

    #[test]
    fn independence_naming_an_unknown_catalyst_is_rejected() {
        let src = P.replace("catalyst a : f() independent b, c;", "catalyst a : f() independent b, zz;");
        assert!(matches!(
            typecheck(&parse(&src).unwrap(), &floors(5.0)),
            Err(Error::UnknownCatalyst { .. })
        ));
    }

    #[test]
    fn duplicate_catalyst_in_via_is_rejected() {
        let src = P.replace("via (a, b, c)", "via (a, a, b)");
        assert!(matches!(
            typecheck(&parse(&src).unwrap(), &floors(5.0)),
            Err(Error::DuplicateCatalyst { .. })
        ));
    }

    #[test]
    fn report_of_unbound_name_is_rejected() {
        let src = P.replace("report x;", "report nope;");
        assert!(matches!(
            typecheck(&parse(&src).unwrap(), &floors(5.0)),
            Err(Error::Unbound { .. })
        ));
    }

    #[test]
    fn missing_floor_warns_rather_than_failing() {
        let d = diagnose(P, &FloorValues::new());
        assert_eq!(d.len(), 1);
        assert_eq!(d[0].severity, Severity::Warning);
        assert!(d[0].message.contains("unchecked"));
    }

    #[test]
    fn diagnose_reports_parse_errors_with_spans() {
        let src = P.replace("excluding rest() ", "");
        let d = diagnose(&src, &floors(5.0));
        assert_eq!(d[0].severity, Severity::Error);
        assert!(d[0].message.contains("excluding"), "{}", d[0].message);
    }
}

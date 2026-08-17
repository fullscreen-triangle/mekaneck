//! LL(1) recursive-descent parser (Paper 3, §4.2, Prop 4.1).
//!
//! One token of lookahead selects a unique production at every point, so the
//! grammar is unambiguous and errors are reported at the token that could not
//! begin a valid production.

use crate::ast::*;
use crate::lex::{lex, Span, Token, TokenKind};
use crate::Error;

pub fn parse(src: &str) -> Result<Program, Error> {
    let tokens = lex(src)?;
    Parser::new(tokens).program()
}

struct Parser {
    toks: Vec<Token>,
    i: usize,
}

impl Parser {
    fn new(toks: Vec<Token>) -> Self {
        Parser { toks, i: 0 }
    }

    fn peek(&self) -> &Token {
        &self.toks[self.i]
    }

    fn bump(&mut self) -> Token {
        let t = self.toks[self.i].clone();
        if self.i + 1 < self.toks.len() {
            self.i += 1;
        }
        t
    }

    fn at_kw(&self, kw: &str) -> bool {
        self.peek().is_keyword(kw)
    }

    fn at_punct(&self, p: &str) -> bool {
        self.peek().is_punct(p)
    }

    fn expect_kw(&mut self, kw: &str) -> Result<Token, Error> {
        if self.at_kw(kw) {
            Ok(self.bump())
        } else {
            Err(Error::Expected {
                what: kw.to_string(),
                found: self.peek().text.clone(),
                span: self.peek().span,
            })
        }
    }

    fn expect_punct(&mut self, p: &str) -> Result<Token, Error> {
        if self.at_punct(p) {
            Ok(self.bump())
        } else {
            Err(Error::Expected {
                what: p.to_string(),
                found: self.peek().text.clone(),
                span: self.peek().span,
            })
        }
    }

    fn expect_ident(&mut self) -> Result<Token, Error> {
        if self.peek().kind == TokenKind::Ident {
            Ok(self.bump())
        } else {
            Err(Error::Expected {
                what: "identifier".to_string(),
                found: self.peek().text.clone(),
                span: self.peek().span,
            })
        }
    }

    fn program(&mut self) -> Result<Program, Error> {
        let mut p = Program::default();
        while self.peek().kind != TokenKind::Eof {
            p.decls.push(if self.at_kw("substrate") {
                Decl::Substrate(self.substrate()?)
            } else if self.at_kw("catalyst") {
                Decl::Catalyst(self.catalyst()?)
            } else if self.at_kw("let") {
                Decl::Let(self.let_decl()?)
            } else if self.at_kw("report") {
                Decl::Report(self.report()?)
            } else {
                return Err(Error::Expected {
                    what: "a declaration (substrate, catalyst, let, report)".into(),
                    found: self.peek().text.clone(),
                    span: self.peek().span,
                });
            });
        }
        Ok(p)
    }

    fn substrate(&mut self) -> Result<SubstrateDecl, Error> {
        let start = self.expect_kw("substrate")?.span;
        let name = self.expect_ident()?.text;
        self.expect_punct("{")?;

        // The four obligations, in a fixed order so that a missing one is
        // reported by name rather than as a generic parse failure.
        let receivers = self.substrate_field("receivers")?;
        let observable = self.substrate_field("observable")?;
        let events = self.substrate_field("events")?;
        let floor = self.substrate_field("floor")?;

        let end = self.expect_punct("}")?.span;
        Ok(SubstrateDecl {
            name,
            receivers,
            observable,
            events,
            floor,
            span: Span::new(start.start, end.end),
        })
    }

    /// One `name : expr ;` obligation inside a substrate block.
    fn substrate_field(&mut self, kw: &str) -> Result<Expr, Error> {
        self.expect_kw(kw)?;
        self.expect_punct(":")?;
        let e = self.expr()?;
        self.expect_punct(";")?;
        Ok(e)
    }

    fn catalyst(&mut self) -> Result<CatalystDecl, Error> {
        let start = self.expect_kw("catalyst")?.span;
        let name = self.expect_ident()?.text;
        self.expect_punct(":")?;
        let body = self.expr()?;
        let independent = if self.at_kw("independent") {
            self.bump();
            self.ident_list()?
        } else {
            Vec::new()
        };
        let end = self.expect_punct(";")?.span;
        Ok(CatalystDecl {
            name,
            body,
            independent,
            span: Span::new(start.start, end.end),
        })
    }

    fn let_decl(&mut self) -> Result<LetDecl, Error> {
        let start = self.expect_kw("let")?.span;
        let name = self.expect_ident()?.text;
        self.expect_punct("=")?;
        let seek = self.seek()?;
        let end = self.expect_punct(";")?.span;
        Ok(LetDecl {
            name,
            seek,
            span: Span::new(start.start, end.end),
        })
    }

    fn report(&mut self) -> Result<ReportDecl, Error> {
        let start = self.expect_kw("report")?.span;
        let name = self.expect_ident()?.text;
        let end = self.expect_punct(";")?.span;
        Ok(ReportDecl {
            name,
            span: Span::new(start.start, end.end),
        })
    }

    fn seek(&mut self) -> Result<SeekExpr, Error> {
        let start = self.expect_kw("seek")?.span;
        let target = self.expr()?;

        // Thm 4.3 / Cor 4.4: a seek without an exclusion clause is not a
        // recoverable parse error but a form the language does not contain.
        // The message says why rather than listing expected tokens.
        if !self.at_kw("excluding") {
            return Err(Error::MissingExclusion {
                span: self.peek().span,
            });
        }
        self.bump();
        let excluding = self.expr()?;

        let (via, via_span) = if self.at_kw("via") {
            let vs = self.bump().span;
            self.expect_punct("(")?;
            let names = self.ident_list()?;
            let close = self.expect_punct(")")?.span;
            (names, Some(Span::new(vs.start, close.end)))
        } else {
            (Vec::new(), None)
        };

        self.expect_kw("until")?;
        let end = self.expect_kw("closure")?.span;

        Ok(SeekExpr {
            target,
            excluding,
            via,
            via_span,
            span: Span::new(start.start, end.end),
        })
    }

    fn ident_list(&mut self) -> Result<Vec<String>, Error> {
        let mut v = vec![self.expect_ident()?.text];
        while self.at_punct(",") {
            self.bump();
            v.push(self.expect_ident()?.text);
        }
        Ok(v)
    }

    fn expr(&mut self) -> Result<Expr, Error> {
        let t = self.peek().clone();
        match t.kind {
            TokenKind::Str => {
                self.bump();
                Ok(Expr::Str {
                    value: t.text,
                    span: t.span,
                })
            }
            TokenKind::Number => {
                self.bump();
                let value = t.text.parse::<f64>().map_err(|_| Error::MalformedNumber {
                    text: t.text.clone(),
                    span: t.span,
                })?;
                Ok(Expr::Number { value, span: t.span })
            }
            TokenKind::Ident => {
                self.bump();
                if self.at_punct("(") {
                    self.bump();
                    let mut args = Vec::new();
                    if !self.at_punct(")") {
                        args.push(self.expr()?);
                        while self.at_punct(",") {
                            self.bump();
                            args.push(self.expr()?);
                        }
                    }
                    let close = self.expect_punct(")")?.span;
                    Ok(Expr::Call {
                        name: t.text,
                        args,
                        span: Span::new(t.span.start, close.end),
                    })
                } else {
                    Ok(Expr::Ident {
                        name: t.text,
                        span: t.span,
                    })
                }
            }
            _ => Err(Error::Expected {
                what: "an expression".into(),
                found: t.text,
                span: t.span,
            }),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const GOOD: &str = r#"
substrate Osc {
  receivers  : recordings("cohort-A");
  observable : coherence_index();
  events     : label_change();
  floor      : asymptotic_separation();
}
catalyst spectral  : band_decomposition() independent surrogate, phase;
catalyst surrogate : phase_randomised()   independent spectral, phase;
catalyst phase     : locking_value()      independent spectral, surrogate;
let regime = seek target_state("hi") excluding all_other() via (spectral, surrogate, phase) until closure;
report regime;
"#;

    #[test]
    fn parses_a_well_formed_program() {
        let p = parse(GOOD).unwrap();
        assert_eq!(p.substrates().count(), 1);
        assert_eq!(p.catalysts().count(), 3);
        assert_eq!(p.lets().count(), 1);
        assert_eq!(p.reports().count(), 1);
        let l = p.lets().next().unwrap();
        assert_eq!(l.seek.via, vec!["spectral", "surrogate", "phase"]);
    }

    #[test]
    fn seek_without_excluding_is_rejected() {
        // Cor 4.4: rejected at parse time, before typing.
        let src = GOOD.replace("excluding all_other() ", "");
        match parse(&src) {
            Err(Error::MissingExclusion { .. }) => {}
            other => panic!("expected MissingExclusion, got {other:?}"),
        }
    }

    #[test]
    fn via_clause_is_optional() {
        let src = r#"
substrate S { receivers : r(); observable : o(); events : e(); floor : f(); }
let x = seek t() excluding rest() until closure;
report x;
"#;
        let p = parse(src).unwrap();
        assert!(p.lets().next().unwrap().seek.via.is_empty());
    }

    #[test]
    fn missing_substrate_field_names_the_field() {
        let src = "substrate S { receivers : r(); observable : o(); floor : f(); }";
        match parse(src) {
            Err(Error::Expected { what, .. }) => assert_eq!(what, "events"),
            other => panic!("expected a field error, got {other:?}"),
        }
    }

    #[test]
    fn nested_calls_parse() {
        let src = r#"
substrate S { receivers : r(); observable : o(); events : e(); floor : f(); }
let x = seek t(u("a"), 1.5) excluding rest() until closure;
report x;
"#;
        let p = parse(src).unwrap();
        let target = p.lets().next().unwrap().seek.target.clone();
        match target {
            Expr::Call { name, args, .. } => {
                assert_eq!(name, "t");
                assert_eq!(args.len(), 2);
            }
            other => panic!("expected a call, got {other:?}"),
        }
    }

    #[test]
    fn spans_point_at_the_offending_token() {
        let src = "substrate 123 {}";
        match parse(src) {
            Err(Error::Expected { span, .. }) => {
                assert_eq!(&src[span.start..span.end], "123");
            }
            other => panic!("expected a span, got {other:?}"),
        }
    }
}

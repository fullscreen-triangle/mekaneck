//! AST for `.mck` (Paper 3, §4).

use serde::{Deserialize, Serialize};

use crate::lex::Span;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Expr {
    Ident { name: String, span: Span },
    Str { value: String, span: Span },
    Number { value: f64, span: Span },
    Call { name: String, args: Vec<Expr>, span: Span },
}

impl Expr {
    pub fn span(&self) -> Span {
        match self {
            Expr::Ident { span, .. }
            | Expr::Str { span, .. }
            | Expr::Number { span, .. }
            | Expr::Call { span, .. } => *span,
        }
    }

    /// The head name, for substrate obligations that name a builtin.
    pub fn head(&self) -> Option<&str> {
        match self {
            Expr::Ident { name, .. } | Expr::Call { name, .. } => Some(name),
            _ => None,
        }
    }
}

/// A substrate declaration: the four obligations of Def 3.1.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SubstrateDecl {
    pub name: String,
    pub receivers: Expr,
    pub observable: Expr,
    pub events: Expr,
    /// Obligation S4. Which estimator this names is the substantive
    /// declaration (Rem 3.2): only a falsifiable one can fail.
    pub floor: Expr,
    pub span: Span,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct CatalystDecl {
    pub name: String,
    pub body: Expr,
    /// Catalysts this one is *declared* independent of. The language cannot
    /// verify the claim (Rem 6.3); it requires it to be written down.
    pub independent: Vec<String>,
    pub span: Span,
}

/// The single computational primitive.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SeekExpr {
    pub target: Expr,
    /// Mandatory. A positive description alone does not determine a target
    /// (Thm 4.3), so this field is not `Option`.
    pub excluding: Expr,
    pub via: Vec<String>,
    pub via_span: Option<Span>,
    pub span: Span,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct LetDecl {
    pub name: String,
    pub seek: SeekExpr,
    pub span: Span,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ReportDecl {
    pub name: String,
    pub span: Span,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Decl {
    Substrate(SubstrateDecl),
    Catalyst(CatalystDecl),
    Let(LetDecl),
    Report(ReportDecl),
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct Program {
    pub decls: Vec<Decl>,
}

impl Program {
    pub fn substrates(&self) -> impl Iterator<Item = &SubstrateDecl> {
        self.decls.iter().filter_map(|d| match d {
            Decl::Substrate(s) => Some(s),
            _ => None,
        })
    }

    pub fn catalysts(&self) -> impl Iterator<Item = &CatalystDecl> {
        self.decls.iter().filter_map(|d| match d {
            Decl::Catalyst(c) => Some(c),
            _ => None,
        })
    }

    pub fn lets(&self) -> impl Iterator<Item = &LetDecl> {
        self.decls.iter().filter_map(|d| match d {
            Decl::Let(l) => Some(l),
            _ => None,
        })
    }

    pub fn reports(&self) -> impl Iterator<Item = &ReportDecl> {
        self.decls.iter().filter_map(|d| match d {
            Decl::Report(r) => Some(r),
            _ => None,
        })
    }
}

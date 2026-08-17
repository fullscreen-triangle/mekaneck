//! Tokenizer for `.mck` (Paper 3, Def 4.1).
//!
//! Every token carries a byte span so that diagnostics can point at source
//! rather than describe it — the web editor consumes these spans directly.

use serde::{Deserialize, Serialize};

use crate::Error;

/// Reserved words. `excluding` is here rather than being contextual because a
/// `seek` without it is a form the language does not contain (Thm 4.3), and a
/// reserved word makes the parse error say so.
pub const KEYWORDS: &[&str] = &[
    "substrate",
    "receivers",
    "observable",
    "events",
    "floor",
    "catalyst",
    "independent",
    "let",
    "seek",
    "excluding",
    "via",
    "until",
    "closure",
    "report",
    "resolved",
    "decline",
    "record",
];

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TokenKind {
    Keyword,
    Ident,
    Number,
    Str,
    Punct,
    Eof,
}

/// Byte offsets into the source, half-open.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct Span {
    pub start: usize,
    pub end: usize,
}

impl Span {
    pub fn new(start: usize, end: usize) -> Self {
        Span { start, end }
    }

    /// 1-based (line, column) for this span's start.
    pub fn line_col(&self, src: &str) -> (usize, usize) {
        let mut line = 1;
        let mut col = 1;
        for (i, ch) in src.char_indices() {
            if i >= self.start {
                break;
            }
            if ch == '\n' {
                line += 1;
                col = 1;
            } else {
                col += 1;
            }
        }
        (line, col)
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Token {
    pub kind: TokenKind,
    pub text: String,
    pub span: Span,
}

impl Token {
    pub fn is_keyword(&self, kw: &str) -> bool {
        self.kind == TokenKind::Keyword && self.text == kw
    }

    pub fn is_punct(&self, p: &str) -> bool {
        self.kind == TokenKind::Punct && self.text == p
    }
}

/// Tokenize. Comments run from `#` to end of line and are discarded;
/// whitespace is insignificant except as a separator.
pub fn lex(src: &str) -> Result<Vec<Token>, Error> {
    let b = src.as_bytes();
    let mut out = Vec::new();
    let mut i = 0usize;

    while i < b.len() {
        let c = b[i];

        if c.is_ascii_whitespace() {
            i += 1;
            continue;
        }
        if c == b'#' {
            while i < b.len() && b[i] != b'\n' {
                i += 1;
            }
            continue;
        }
        if c == b'"' {
            let start = i;
            i += 1;
            while i < b.len() && b[i] != b'"' {
                if b[i] == b'\n' {
                    return Err(Error::UnterminatedString(Span::new(start, i)));
                }
                i += 1;
            }
            if i >= b.len() {
                return Err(Error::UnterminatedString(Span::new(start, b.len())));
            }
            i += 1; // closing quote
            out.push(Token {
                kind: TokenKind::Str,
                text: src[start + 1..i - 1].to_string(),
                span: Span::new(start, i),
            });
            continue;
        }
        if c.is_ascii_digit() {
            let start = i;
            while i < b.len() && (b[i].is_ascii_digit() || b[i] == b'.') {
                i += 1;
            }
            let text = &src[start..i];
            if text.matches('.').count() > 1 {
                return Err(Error::MalformedNumber {
                    text: text.to_string(),
                    span: Span::new(start, i),
                });
            }
            out.push(Token {
                kind: TokenKind::Number,
                text: text.to_string(),
                span: Span::new(start, i),
            });
            continue;
        }
        if c.is_ascii_alphabetic() || c == b'_' {
            let start = i;
            while i < b.len() && (b[i].is_ascii_alphanumeric() || b[i] == b'_') {
                i += 1;
            }
            let text = &src[start..i];
            out.push(Token {
                kind: if KEYWORDS.contains(&text) {
                    TokenKind::Keyword
                } else {
                    TokenKind::Ident
                },
                text: text.to_string(),
                span: Span::new(start, i),
            });
            continue;
        }
        if matches!(c, b'{' | b'}' | b'(' | b')' | b',' | b';' | b':' | b'=') {
            out.push(Token {
                kind: TokenKind::Punct,
                text: (c as char).to_string(),
                span: Span::new(i, i + 1),
            });
            i += 1;
            continue;
        }

        return Err(Error::UnexpectedChar {
            ch: c as char,
            span: Span::new(i, i + 1),
        });
    }

    out.push(Token {
        kind: TokenKind::Eof,
        text: String::new(),
        span: Span::new(b.len(), b.len()),
    });
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn keywords_are_distinguished_from_identifiers() {
        let t = lex("seek target").unwrap();
        assert_eq!(t[0].kind, TokenKind::Keyword);
        assert_eq!(t[1].kind, TokenKind::Ident);
    }

    #[test]
    fn comments_and_whitespace_are_discarded() {
        let t = lex("  # a comment\n  let  ").unwrap();
        assert_eq!(t.len(), 2); // let, EOF
        assert!(t[0].is_keyword("let"));
    }

    #[test]
    fn strings_and_numbers() {
        let t = lex(r#"f("abc", 1.5)"#).unwrap();
        let kinds: Vec<_> = t.iter().map(|x| x.kind).collect();
        assert_eq!(
            kinds,
            vec![
                TokenKind::Ident,
                TokenKind::Punct,
                TokenKind::Str,
                TokenKind::Punct,
                TokenKind::Number,
                TokenKind::Punct,
                TokenKind::Eof
            ]
        );
        assert_eq!(t[2].text, "abc");
    }

    #[test]
    fn unterminated_string_is_reported_with_a_span() {
        match lex("f(\"abc)") {
            Err(Error::UnterminatedString(s)) => assert_eq!(s.start, 2),
            other => panic!("expected UnterminatedString, got {other:?}"),
        }
    }

    #[test]
    fn malformed_number_is_reported() {
        assert!(matches!(lex("1.2.3"), Err(Error::MalformedNumber { .. })));
    }

    #[test]
    fn unexpected_character_is_reported() {
        assert!(matches!(lex("let x @ y"), Err(Error::UnexpectedChar { .. })));
    }

    #[test]
    fn spans_map_to_line_and_column() {
        let src = "let\n  seek";
        let t = lex(src).unwrap();
        assert_eq!(t[1].span.line_col(src), (2, 3));
    }
}

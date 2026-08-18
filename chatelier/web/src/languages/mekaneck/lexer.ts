/**
 * Tokenizer for `.mck`.
 *
 * A mirror of `crates/lang/src/lex.rs`. It exists so the editor can mark
 * errors without a round trip to the binary; it is NOT authoritative. Both
 * implementations are pinned to `fixtures.json`, which the Rust generates —
 * if the two diverge, the shared suite fails on both sides.
 *
 * Spans are byte offsets to match Rust exactly. For ASCII source these equal
 * character offsets; the `.mck` grammar is ASCII-only, and non-ASCII bytes are
 * rejected by the lexer, so the two never disagree.
 */

export const KEYWORDS = [
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
] as const;

export type TokenKind = "keyword" | "ident" | "number" | "str" | "punct" | "eof";

export interface Span {
  start: number;
  end: number;
}

export interface Token {
  kind: TokenKind;
  text: string;
  span: Span;
}

/** A lexical or syntactic failure, carrying the span it applies to. */
export class MckError extends Error {
  constructor(
    message: string,
    readonly span: Span,
  ) {
    super(message);
    this.name = "MckError";
  }
}

const PUNCT = new Set(["{", "}", "(", ")", ",", ";", ":", "="]);

const isDigit = (c: string) => c >= "0" && c <= "9";
const isAlpha = (c: string) =>
  (c >= "a" && c <= "z") || (c >= "A" && c <= "Z") || c === "_";
const isAlnum = (c: string) => isAlpha(c) || isDigit(c);
const isSpace = (c: string) =>
  c === " " || c === "\t" || c === "\n" || c === "\r" || c === "\x0b" || c === "\x0c";

export function lex(src: string): Token[] {
  const out: Token[] = [];
  let i = 0;

  while (i < src.length) {
    const c = src[i];

    if (isSpace(c)) {
      i += 1;
      continue;
    }
    // Comments run to end of line and are discarded.
    if (c === "#") {
      while (i < src.length && src[i] !== "\n") i += 1;
      continue;
    }
    if (c === '"') {
      const start = i;
      i += 1;
      while (i < src.length && src[i] !== '"') {
        if (src[i] === "\n") {
          throw new MckError("unterminated string literal", { start, end: i });
        }
        i += 1;
      }
      if (i >= src.length) {
        throw new MckError("unterminated string literal", {
          start,
          end: src.length,
        });
      }
      i += 1; // closing quote
      out.push({
        kind: "str",
        text: src.slice(start + 1, i - 1),
        span: { start, end: i },
      });
      continue;
    }
    if (isDigit(c)) {
      const start = i;
      while (i < src.length && (isDigit(src[i]) || src[i] === ".")) i += 1;
      const text = src.slice(start, i);
      if ((text.match(/\./g) ?? []).length > 1) {
        throw new MckError(`malformed number "${text}"`, { start, end: i });
      }
      out.push({ kind: "number", text, span: { start, end: i } });
      continue;
    }
    if (isAlpha(c)) {
      const start = i;
      while (i < src.length && isAlnum(src[i])) i += 1;
      const text = src.slice(start, i);
      out.push({
        kind: (KEYWORDS as readonly string[]).includes(text) ? "keyword" : "ident",
        text,
        span: { start, end: i },
      });
      continue;
    }
    if (PUNCT.has(c)) {
      out.push({ kind: "punct", text: c, span: { start: i, end: i + 1 } });
      i += 1;
      continue;
    }

    throw new MckError(`unexpected character '${c}'`, { start: i, end: i + 1 });
  }

  out.push({ kind: "eof", text: "", span: { start: src.length, end: src.length } });
  return out;
}

/** 1-based line and column for a span's start, matching `Span::line_col`. */
export function lineCol(src: string, span: Span): { line: number; column: number } {
  let line = 1;
  let column = 1;
  for (let i = 0; i < src.length && i < span.start; i += 1) {
    if (src[i] === "\n") {
      line += 1;
      column = 1;
    } else {
      column += 1;
    }
  }
  return { line, column };
}

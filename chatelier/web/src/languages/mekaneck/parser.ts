/**
 * LL(1) parser for `.mck`.
 *
 * A mirror of `crates/lang/src/parse.rs`. Error messages are kept
 * character-identical to the Rust where the shared fixtures pin them; the
 * binary remains authoritative, and this exists only so the editor can mark
 * source without a round trip.
 */

import { lex, MckError, type Span, type Token } from "./lexer";

export interface ExprIdent {
  kind: "ident";
  name: string;
  span: Span;
}
export interface ExprStr {
  kind: "str";
  value: string;
  span: Span;
}
export interface ExprNumber {
  kind: "number";
  value: number;
  span: Span;
}
export interface ExprCall {
  kind: "call";
  name: string;
  args: Expr[];
  span: Span;
}
export type Expr = ExprIdent | ExprStr | ExprNumber | ExprCall;

export interface SubstrateDecl {
  kind: "substrate";
  name: string;
  receivers: Expr;
  observable: Expr;
  events: Expr;
  floor: Expr;
  span: Span;
}

export interface CatalystDecl {
  kind: "catalyst";
  name: string;
  body: Expr;
  independent: string[];
  span: Span;
}

export interface SeekExpr {
  target: Expr;
  /** Mandatory: a target is not determined by a positive description alone. */
  excluding: Expr;
  via: string[];
  viaSpan: Span | null;
  span: Span;
}

export interface LetDecl {
  kind: "let";
  name: string;
  seek: SeekExpr;
  span: Span;
}

export interface ReportDecl {
  kind: "report";
  name: string;
  span: Span;
}

export type Decl = SubstrateDecl | CatalystDecl | LetDecl | ReportDecl;

export interface Program {
  decls: Decl[];
}

export function parse(src: string): Program {
  return new Parser(lex(src)).program();
}

class Parser {
  private i = 0;

  constructor(private readonly toks: Token[]) {}

  private peek(): Token {
    return this.toks[this.i];
  }

  private bump(): Token {
    const t = this.toks[this.i];
    if (this.i + 1 < this.toks.length) this.i += 1;
    return t;
  }

  private atKw(kw: string): boolean {
    const t = this.peek();
    return t.kind === "keyword" && t.text === kw;
  }

  private atPunct(p: string): boolean {
    const t = this.peek();
    return t.kind === "punct" && t.text === p;
  }

  private expected(what: string): never {
    const t = this.peek();
    throw new MckError(`expected ${what}, found "${t.text}"`, t.span);
  }

  private expectKw(kw: string): Token {
    if (!this.atKw(kw)) this.expected(kw);
    return this.bump();
  }

  private expectPunct(p: string): Token {
    if (!this.atPunct(p)) this.expected(p);
    return this.bump();
  }

  private expectIdent(): Token {
    if (this.peek().kind !== "ident") this.expected("identifier");
    return this.bump();
  }

  program(): Program {
    const decls: Decl[] = [];
    while (this.peek().kind !== "eof") {
      if (this.atKw("substrate")) decls.push(this.substrate());
      else if (this.atKw("catalyst")) decls.push(this.catalyst());
      else if (this.atKw("let")) decls.push(this.letDecl());
      else if (this.atKw("report")) decls.push(this.report());
      else this.expected("a declaration (substrate, catalyst, let, report)");
    }
    return { decls };
  }

  private substrateField(kw: string): Expr {
    this.expectKw(kw);
    this.expectPunct(":");
    const e = this.expr();
    this.expectPunct(";");
    return e;
  }

  private substrate(): SubstrateDecl {
    const start = this.expectKw("substrate").span;
    const name = this.expectIdent().text;
    this.expectPunct("{");
    // Fixed order, so a missing obligation is reported by name.
    const receivers = this.substrateField("receivers");
    const observable = this.substrateField("observable");
    const events = this.substrateField("events");
    const floor = this.substrateField("floor");
    const end = this.expectPunct("}").span;
    return {
      kind: "substrate",
      name,
      receivers,
      observable,
      events,
      floor,
      span: { start: start.start, end: end.end },
    };
  }

  private catalyst(): CatalystDecl {
    const start = this.expectKw("catalyst").span;
    const name = this.expectIdent().text;
    this.expectPunct(":");
    const body = this.expr();
    let independent: string[] = [];
    if (this.atKw("independent")) {
      this.bump();
      independent = this.identList();
    }
    const end = this.expectPunct(";").span;
    return {
      kind: "catalyst",
      name,
      body,
      independent,
      span: { start: start.start, end: end.end },
    };
  }

  private letDecl(): LetDecl {
    const start = this.expectKw("let").span;
    const name = this.expectIdent().text;
    this.expectPunct("=");
    const seek = this.seek();
    const end = this.expectPunct(";").span;
    return { kind: "let", name, seek, span: { start: start.start, end: end.end } };
  }

  private report(): ReportDecl {
    const start = this.expectKw("report").span;
    const name = this.expectIdent().text;
    const end = this.expectPunct(";").span;
    return { kind: "report", name, span: { start: start.start, end: end.end } };
  }

  private seek(): SeekExpr {
    const start = this.expectKw("seek").span;
    const target = this.expr();

    // Not a recoverable parse error: a seek without an exclusion clause is a
    // form the language does not contain, and the message says why.
    if (!this.atKw("excluding")) {
      throw new MckError(
        "seek requires an 'excluding' clause: a target is not determined by a " +
          "positive description alone, so a seek without one has no unique denotation",
        this.peek().span,
      );
    }
    this.bump();
    const excluding = this.expr();

    let via: string[] = [];
    let viaSpan: Span | null = null;
    if (this.atKw("via")) {
      const vs = this.bump().span;
      this.expectPunct("(");
      via = this.identList();
      const close = this.expectPunct(")").span;
      viaSpan = { start: vs.start, end: close.end };
    }

    this.expectKw("until");
    const end = this.expectKw("closure").span;
    return { target, excluding, via, viaSpan, span: { start: start.start, end: end.end } };
  }

  private identList(): string[] {
    const v = [this.expectIdent().text];
    while (this.atPunct(",")) {
      this.bump();
      v.push(this.expectIdent().text);
    }
    return v;
  }

  private expr(): Expr {
    const t = this.peek();
    switch (t.kind) {
      case "str":
        this.bump();
        return { kind: "str", value: t.text, span: t.span };
      case "number": {
        this.bump();
        const value = Number(t.text);
        if (Number.isNaN(value)) {
          throw new MckError(`malformed number "${t.text}"`, t.span);
        }
        return { kind: "number", value, span: t.span };
      }
      case "ident": {
        this.bump();
        if (this.atPunct("(")) {
          this.bump();
          const args: Expr[] = [];
          if (!this.atPunct(")")) {
            args.push(this.expr());
            while (this.atPunct(",")) {
              this.bump();
              args.push(this.expr());
            }
          }
          const close = this.expectPunct(")").span;
          return {
            kind: "call",
            name: t.text,
            args,
            span: { start: t.span.start, end: close.end },
          };
        }
        return { kind: "ident", name: t.text, span: t.span };
      }
      default:
        this.expected("an expression");
    }
  }
}

export function exprSpan(e: Expr): Span {
  return e.span;
}

export const substrates = (p: Program): SubstrateDecl[] =>
  p.decls.filter((d): d is SubstrateDecl => d.kind === "substrate");
export const catalysts = (p: Program): CatalystDecl[] =>
  p.decls.filter((d): d is CatalystDecl => d.kind === "catalyst");
export const lets = (p: Program): LetDecl[] =>
  p.decls.filter((d): d is LetDecl => d.kind === "let");
export const reports = (p: Program): ReportDecl[] =>
  p.decls.filter((d): d is ReportDecl => d.kind === "report");

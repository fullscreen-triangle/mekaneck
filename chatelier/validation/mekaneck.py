"""
Reference implementation of Mekaneck (.mck).

Lexer, LL(1) parser, type checker, and small-step evaluator, following the
specification in "Mekaneck: A Substrate-Neutral Language for
Individuation-Structured Inquiry".

The language has one primitive (seek), a mandatory exclusion clause, two
non-standard typing rules (positivity, coherence), and three reduction rules
(E-Invoke, E-Close-Res, E-Close-Dec).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ======================================================================
# Errors
# ======================================================================

class MckSyntaxError(Exception):
    pass


class MckTypeError(Exception):
    pass


# ======================================================================
# Lexer  (Def 4.1)
# ======================================================================

KEYWORDS = {
    "substrate", "receivers", "observable", "events", "floor",
    "catalyst", "independent", "let", "seek", "excluding", "via",
    "until", "closure", "report", "resolved", "decline", "record",
}

TOKEN_SPEC = [
    ("COMMENT", r"\#[^\n]*"),
    ("WS",      r"\s+"),
    ("NUMBER",  r"\d+\.\d+|\d+"),
    ("STRING",  r'"[^"]*"'),
    ("IDENT",   r"[A-Za-z_][A-Za-z0-9_]*"),
    ("PUNCT",   r"[{}(),;:=]"),
]

MASTER_RE = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC))


@dataclass
class Token:
    kind: str
    value: str
    pos: int

    def __repr__(self):
        return f"{self.kind}({self.value})"


def lex(src: str) -> list[Token]:
    tokens, i = [], 0
    while i < len(src):
        m = MASTER_RE.match(src, i)
        if not m:
            raise MckSyntaxError(f"unexpected character {src[i]!r} at {i}")
        kind = m.lastgroup
        val = m.group()
        if kind not in ("WS", "COMMENT"):
            if kind == "IDENT" and val in KEYWORDS:
                kind = "KW"
            tokens.append(Token(kind, val, i))
        i = m.end()
    tokens.append(Token("EOF", "", len(src)))
    return tokens


# ======================================================================
# AST
# ======================================================================

@dataclass
class Expr:
    head: str
    args: list = field(default_factory=list)


@dataclass
class SubstrateDecl:
    name: str
    receivers: Expr
    observable: Expr
    events: Expr
    floor: Expr


@dataclass
class CatalystDecl:
    name: str
    body: Expr
    independent: list = field(default_factory=list)


@dataclass
class SeekExpr:
    target: Expr
    excluding: Expr           # MANDATORY (Thm 4.3)
    via: list
    until: str                # only "closure"


@dataclass
class LetDecl:
    name: str
    seek: SeekExpr


@dataclass
class ReportDecl:
    name: str


@dataclass
class Program:
    decls: list = field(default_factory=list)


# ======================================================================
# Parser  (LL(1), Prop 4.1)
# ======================================================================

class Parser:
    def __init__(self, tokens: list[Token]):
        self.toks = tokens
        self.i = 0

    def peek(self) -> Token:
        return self.toks[self.i]

    def next(self) -> Token:
        t = self.toks[self.i]
        self.i += 1
        return t

    def expect(self, kind: str, value: str | None = None) -> Token:
        t = self.peek()
        if t.kind != kind or (value is not None and t.value != value):
            want = value or kind
            raise MckSyntaxError(
                f"expected {want!r} at position {t.pos}, found {t.value!r}")
        return self.next()

    def at_kw(self, value: str) -> bool:
        t = self.peek()
        return t.kind == "KW" and t.value == value

    # -- program -------------------------------------------------------
    def parse_program(self) -> Program:
        prog = Program()
        while self.peek().kind != "EOF":
            if self.at_kw("substrate"):
                prog.decls.append(self.parse_substrate())
            elif self.at_kw("catalyst"):
                prog.decls.append(self.parse_catalyst())
            elif self.at_kw("let"):
                prog.decls.append(self.parse_let())
            elif self.at_kw("report"):
                prog.decls.append(self.parse_report())
            else:
                t = self.peek()
                raise MckSyntaxError(
                    f"expected a declaration at {t.pos}, found {t.value!r}")
        return prog

    def parse_substrate(self) -> SubstrateDecl:
        self.expect("KW", "substrate")
        name = self.expect("IDENT").value
        self.expect("PUNCT", "{")
        fields = {}
        for key in ("receivers", "observable", "events", "floor"):
            self.expect("KW", key)
            self.expect("PUNCT", ":")
            fields[key] = self.parse_expr()
            self.expect("PUNCT", ";")
        self.expect("PUNCT", "}")
        return SubstrateDecl(name, fields["receivers"], fields["observable"],
                             fields["events"], fields["floor"])

    def parse_catalyst(self) -> CatalystDecl:
        self.expect("KW", "catalyst")
        name = self.expect("IDENT").value
        self.expect("PUNCT", ":")
        body = self.parse_expr()
        indep = []
        if self.at_kw("independent"):
            self.next()
            indep = self.parse_ident_list()
        self.expect("PUNCT", ";")
        return CatalystDecl(name, body, indep)

    def parse_let(self) -> LetDecl:
        self.expect("KW", "let")
        name = self.expect("IDENT").value
        self.expect("PUNCT", "=")
        seek = self.parse_seek()
        self.expect("PUNCT", ";")
        return LetDecl(name, seek)

    def parse_report(self) -> ReportDecl:
        self.expect("KW", "report")
        name = self.expect("IDENT").value
        self.expect("PUNCT", ";")
        return ReportDecl(name)

    def parse_seek(self) -> SeekExpr:
        self.expect("KW", "seek")
        target = self.parse_expr()
        # MANDATORY exclusion clause -- Thm 4.3 / Cor 4.4
        if not self.at_kw("excluding"):
            t = self.peek()
            raise MckSyntaxError(
                f"seek requires an 'excluding' clause (position {t.pos}): a target "
                f"is not determined by a positive description alone")
        self.expect("KW", "excluding")
        excl = self.parse_expr()

        via = []
        if self.at_kw("via"):
            self.next()
            self.expect("PUNCT", "(")
            via = self.parse_ident_list()
            self.expect("PUNCT", ")")

        self.expect("KW", "until")
        self.expect("KW", "closure")
        return SeekExpr(target, excl, via, "closure")

    def parse_ident_list(self) -> list:
        names = [self.expect("IDENT").value]
        while self.peek().kind == "PUNCT" and self.peek().value == ",":
            self.next()
            names.append(self.expect("IDENT").value)
        return names

    def parse_expr(self) -> Expr:
        t = self.peek()
        if t.kind == "STRING":
            self.next()
            return Expr("string", [t.value.strip('"')])
        if t.kind == "NUMBER":
            self.next()
            return Expr("number", [float(t.value)])
        if t.kind == "IDENT":
            self.next()
            if self.peek().kind == "PUNCT" and self.peek().value == "(":
                self.next()
                args = []
                if not (self.peek().kind == "PUNCT" and self.peek().value == ")"):
                    args.append(self.parse_expr())
                    while self.peek().kind == "PUNCT" and self.peek().value == ",":
                        self.next()
                        args.append(self.parse_expr())
                self.expect("PUNCT", ")")
                return Expr("call", [t.value, args])
            return Expr("ident", [t.value])
        raise MckSyntaxError(f"expected an expression at {t.pos}, found {t.value!r}")


def parse(src: str) -> Program:
    return Parser(lex(src)).parse_program()


# ======================================================================
# Type checker  (Sec 5)
# ======================================================================

@dataclass
class TypeEnv:
    substrates: dict = field(default_factory=dict)
    catalysts: dict = field(default_factory=dict)     # name -> independent list
    bindings: dict = field(default_factory=dict)      # name -> type


def typecheck(prog: Program, floor_values: dict | None = None) -> TypeEnv:
    """
    floor_values maps substrate name -> numeric floor supplied by the binding.
    T-Seek-Pos requires it to be strictly positive.
    """
    floor_values = floor_values or {}
    env = TypeEnv()

    for d in prog.decls:
        if isinstance(d, SubstrateDecl):
            env.substrates[d.name] = d
            env.bindings[d.name] = "Substrate"
        elif isinstance(d, CatalystDecl):
            env.catalysts[d.name] = list(d.independent)
            env.bindings[d.name] = "Catalyst"

    # forward reference check for independence declarations
    for name, indep in env.catalysts.items():
        for other in indep:
            if other not in env.catalysts:
                raise MckTypeError(
                    f"catalyst {name!r} declares independence from unknown "
                    f"catalyst {other!r}")

    for d in prog.decls:
        if isinstance(d, LetDecl):
            _check_seek(d.seek, env, floor_values)
            env.bindings[d.name] = "Outcome"
        elif isinstance(d, ReportDecl):
            if d.name not in env.bindings:
                raise MckTypeError(f"report of unbound identifier {d.name!r}")
    return env


def _check_seek(seek: SeekExpr, env: TypeEnv, floor_values: dict) -> None:
    # ---- T-Seek-Pos (Def 5.3): the floor must be strictly positive --------
    if not env.substrates:
        raise MckTypeError("no substrate declared: seek has no floor obligation")
    for sname in env.substrates:
        beta = floor_values.get(sname)
        if beta is None:
            continue
        if beta <= 0:
            raise MckTypeError(
                f"T-Seek-Pos: substrate {sname!r} declares floor {beta} <= 0; "
                f"a program may not assert an attainable zero residual")

    # ---- T-Seek-Coh (Def 5.4): >= 3 mutually independent catalysts -------
    if seek.via:
        for c in seek.via:
            if c not in env.catalysts:
                raise MckTypeError(f"unknown catalyst {c!r} in via clause")
        if len(seek.via) < 3:
            raise MckTypeError(
                f"T-Seek-Coh: via names {len(seek.via)} catalyst(s); a robust "
                f"support structure requires at least 3 (a 1-cycle is vacuous, "
                f"a 2-cycle collapses on removal of either member)")
        for a in seek.via:
            for b in seek.via:
                if a == b:
                    continue
                if b not in env.catalysts[a]:
                    raise MckTypeError(
                        f"T-Seek-Coh: catalysts {a!r} and {b!r} are not mutually "
                        f"declared independent")


# ======================================================================
# Evaluator  (Sec 6)
# ======================================================================

@dataclass
class Config:
    """Configuration <e, store, record>  (Def 6.1)."""
    available: list
    reached: set = field(default_factory=set)
    record: int = 0
    outcome: Any = None
    trace: list = field(default_factory=list)


@dataclass
class Resolved:
    cell: str

    def __repr__(self):
        return f"Resolved({self.cell})"


@dataclass
class Declined:
    cells: tuple

    def __repr__(self):
        return f"Declined({sorted(self.cells)})"


def evaluate(seek: SeekExpr, substrate: dict, order: list | None = None) -> Config:
    """
    substrate maps catalyst name -> cell it yields.
    Reduction rules: E-Invoke, E-Close-Res, E-Close-Dec.
    """
    avail = list(order) if order else list(seek.via)
    cfg = Config(available=avail)

    while True:
        # closure test: does any remaining catalyst add a NEW cell?
        adds_new = [c for c in cfg.available
                    if substrate.get(c) not in cfg.reached]

        if not adds_new:
            if len(cfg.reached) == 0:
                # nothing invoked yet and nothing available: vacuous
                cfg.outcome = Declined(tuple())
                return cfg
            if len(cfg.reached) == 1:                       # E-Close-Res
                cfg.outcome = Resolved(next(iter(cfg.reached)))
            else:                                            # E-Close-Dec
                cfg.outcome = Declined(tuple(sorted(cfg.reached)))
            return cfg

        c = adds_new[0]                                      # E-Invoke
        cell = substrate.get(c)
        cfg.reached.add(cell)
        cfg.available.remove(c)
        cfg.record += 1
        cfg.trace.append({"invoked": c, "cell": cell, "record": cfg.record})


def evaluate_threshold(seek: SeekExpr, substrate: dict,
                       uncertainty: dict, theta: float,
                       order: list | None = None) -> Config:
    """
    Contrast procedure: stop as soon as attained uncertainty < theta.
    Used to demonstrate Thm 6.6 (closure strictly stronger).
    """
    avail = list(order) if order else list(seek.via)
    cfg = Config(available=avail)
    for c in avail:
        cell = substrate.get(c)
        cfg.reached.add(cell)
        cfg.record += 1
        cfg.trace.append({"invoked": c, "cell": cell, "record": cfg.record})
        if uncertainty.get(cell, float("inf")) < theta:
            cfg.outcome = Resolved(cell)
            return cfg
    cfg.outcome = (Resolved(next(iter(cfg.reached))) if len(cfg.reached) == 1
                   else Declined(tuple(sorted(cfg.reached))))
    return cfg

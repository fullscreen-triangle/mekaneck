# Mekaneck

Implementation of the three papers in [`docs/`](docs/):

| Paper | Crate | What it is |
|---|---|---|
| *A Residual Algebra for Catalytic Composition* | `mekaneck-algebra` | derived floors, catalytic power, composition, closure |
| *A Semantically Inert Microkernel* | `mekaneck-kernel` *(not yet built)* | judgement-free runtime |
| *Mekaneck: A Substrate-Neutral Language* | `mekaneck-lang` | the `.mck` compiler |

## Status

Built and tested: **algebra**, **lang**, **cli** — 71 tests, zero clippy warnings.
Not yet built: kernel, substrates, server, web IDE.

## Quick start

```bash
cargo build --release
./target/release/mekaneck check examples/coherence.mck --floor Osc=12.5
```

## Why you run this locally

The binary listens on loopback only and never dials out. The web IDE connects
*to* your machine, so analysis data does not leave the host — the token is a
loopback handshake secret, not an account credential. Downloading and running
the binary is the intended path; the hosted editor is a front end for it.

## The CLI

```bash
mekaneck check FILE  --floor NAME=VALUE        # parse + typecheck
mekaneck run   FILE  --floor NAME=VALUE --cell CATALYST=CELL
mekaneck floor FILE  --estimator asymptotic    # estimate a floor from stages
mekaneck tokens FILE                            # token stream, for editor work
```

All commands take `--json` for machine-readable output.

### What the compiler refuses

Three rejections are structural rather than stylistic, and each reports the
reason rather than a token list:

```console
$ mekaneck check no-exclusion.mck --floor Osc=12.5
no-exclusion.mck:23:3: error: seek requires an 'excluding' clause: a target is not
determined by a positive description alone, so a seek without one has no unique
denotation

$ mekaneck check two-catalysts.mck --floor Osc=12.5
two-catalysts.mck:23:3: error: via names 2 catalyst(s); a support structure robust
to the loss of any one member needs at least 3 (a 1-cycle is vacuous, a 2-cycle
collapses)

$ mekaneck check coherence.mck --floor Osc=0
coherence.mck:11:16: error: substrate "Osc" declares floor 0, which is not strictly
positive: a program may not assert an attainable zero residual
```

### Two terminations, both normal

An inquiry ends in exactly one of two states, and **declination exits 0** — it
is a result, not a failure:

```console
$ mekaneck run examples/coherence.mck --floor Osc=12.5 \
    --cell spectral=high --cell surrogate=high --cell phase=high
regime: resolved high  (record 1)

$ mekaneck run examples/coherence.mck --floor Osc=12.5 \
    --cell spectral=high --cell surrogate=high --cell phase=mixed
regime: declined, 2 incompatible cells  (record 2)
    high  via spectral
    mixed via phase
```

The second run is the case a confidence threshold gets wrong: it would have
stopped after `spectral` reported a confident cell and never consulted `phase`.

### Floor estimation

```console
$ mekaneck floor data/unfloored.json --estimator sample-minimum
floor: 0.000000
note: this estimator is bounded below by the sample and cannot return a
non-positive value, so its positivity is not evidence for a positive floor
```

The note is unprompted by design. The two estimators differ in kind, not in
accuracy — on a floored process the sample minimum is often *more* accurate,
but it cannot produce evidence against `β > 0`, and it is biased upward, which
inflates the powers of exactly the events acting nearest the floor.

## What the types enforce

Three results from the papers are carried by the type system rather than left
to caller discipline:

- `Floor` cannot hold a non-positive value, so the denominator of the power
  definition is never zero.
- `Estimation` travels with every prediction, and `CompositionTest::is_evidential()`
  is **false** under instance-specific estimation however good the agreement
  looks. This is the telescoping obstruction: that comparison is an algebraic
  identity that reports `r = 1.000` on data from any process whatsoever.
- `FloorEstimator` records whether an estimate *could* have come out
  non-positive, so a reported positive floor carries its own evidential status.

## Layout

```
chatelier/
├── Cargo.toml            workspace root
├── crates/
│   ├── algebra/          residual, power, compose, cascade, diagnose
│   ├── lang/             lex, parse, types, eval, ast
│   └── cli/              the `mekaneck` binary
├── examples/             .mck programs and fixture data
├── docs/                 the three papers + figure panels
└── validation/           Python suites the Rust conforms to
```

## Conformance

`crates/algebra/tests/conformance.rs` asserts values the Python suites also
produce — the telescoping deviation bound of `2.22e-16`, the closed form
`1/(n+1)`, the summable limit `0.2887880950866024`, and the closure-vs-threshold
invocation counts. The two implementations cannot drift apart silently.

```bash
cargo test                                   # Rust, 71 tests
python validation/run_all.py                 # Python, 21 checks
```

## Next

- `kernel` — nodes, inertia, convergence, protocol fingerprint, scheduler
- `substrates` — the four obligations as a trait, with three bindings
- `server` — loopback WebSocket, token handshake
- `web` — Next.js IDE; TypeScript mirrors lex/parse/typecheck for instant
  diagnostics, with a shared conformance suite against the Rust to prevent
  drift. Evaluation stays in the local binary.

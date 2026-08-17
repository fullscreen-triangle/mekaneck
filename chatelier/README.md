# Mekaneck

Implementation of the three papers in [`docs/`](docs/):

| Paper | Crate | What it is |
|---|---|---|
| *A Residual Algebra for Catalytic Composition* | `mekaneck-algebra` | derived floors, catalytic power, composition, closure |
| *A Semantically Inert Microkernel* | `mekaneck-kernel` | judgement-free runtime |
| *Mekaneck: A Substrate-Neutral Language* | `mekaneck-lang` | the `.mck` compiler |

## Status

Built and tested: **algebra**, **kernel**, **lang**, **substrates**, **cli** —
115 tests, zero clippy warnings.
Not yet built: server (loopback WebSocket + token), web IDE.

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
mekaneck check   FILE --floor NAME=VALUE        # parse + typecheck
mekaneck run     FILE --floor NAME=VALUE --cell CATALYST=CELL
mekaneck floor   FILE --estimator asymptotic    # estimate a floor from stages
mekaneck analyse FILE                           # full pipeline over a substrate
mekaneck tokens  FILE                           # token stream, for editor work
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

### The analysis the apparatus exists for

`analyse` runs a substrate through floor estimation, cascade extraction and the
law comparison, and reports **both** estimation regimes side by side:

```console
$ mekaneck analyse examples/data/sleep_substrate.json
cascades: 40   types: 20   eta: 0.9635

law              estimation                  r       rmse     evid
multiplicative   instance_specific      1.0000     0.0000       NO
multiplicative   type_averaged          0.9847     0.0232      yes
additive         type_averaged          0.8112     0.1733      yes
geometric_mean   type_averaged          0.8417     0.4474      yes
maximum          type_averaged          0.7671     0.2937      yes
```

The first row is the trap the papers exist to name: a perfect `r = 1.0000`
that is an algebraic identity, marked `evid=NO`. The row beneath it is the
same law tested properly. `eta` is printed alongside because a law comparison
below the flagging threshold cannot adjudicate the typing, however good `r`
looks.

## Layout

```
chatelier/
├── Cargo.toml            workspace root
├── crates/
│   ├── algebra/          residual, power, compose, cascade, diagnose
│   ├── kernel/           node, graph, exec, schedule, trajectory
│   ├── lang/             lex, parse, types, eval, ast
│   ├── substrates/       the four obligations as a trait + bindings
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
cargo test                                   # Rust, 115 tests
python validation/run_all.py                 # Python, 21 checks
```

The kernel's conformance suite additionally pins the inertia counts (5 chunks,
2 errors, 3 normal), the convergence result (1 protocol over 6 merge orders,
4 chunks on the shared identity), and the scheduler numbers (12 executions,
record 36, late chunk served in one step).

## Next

- `server` — loopback WebSocket, token handshake
- `web` — Next.js IDE; TypeScript mirrors lex/parse/typecheck for instant
  diagnostics, with a shared conformance suite against the Rust to prevent
  drift. Evaluation stays in the local binary.

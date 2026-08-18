# Mekaneck

Implementation of the three papers in [`docs/`](docs/):

| Paper | Crate | What it is |
|---|---|---|
| *A Residual Algebra for Catalytic Composition* | `mekaneck-algebra` | derived floors, catalytic power, composition, closure |
| *A Semantically Inert Microkernel* | `mekaneck-kernel` | judgement-free runtime |
| *Mekaneck: A Substrate-Neutral Language* | `mekaneck-lang` | the `.mck` compiler |

## Status

Built and tested: **algebra**, **kernel**, **lang**, **substrates**, **server**,
**cli**, and the **web interface** — 157 Rust tests, 40 TypeScript tests, 21
Python checks, and 19 live end-to-end server checks. Zero clippy warnings,
TypeScript compiles clean.

The web layer includes the connection client, the language services, and the
result panels. See [web/README.md](web/README.md) for the three display
constraints it enforces and the tests that hold it to them.

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
mekaneck serve        --port 8731             # loopback IDE server + token
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

## Pairing a browser with your binary

```console
$ mekaneck serve
mekaneck is listening on http://127.0.0.1:8731

  token: 3169bd90f4ec79ff47512c469852bebc339d221c59c653d8e10d1ad10e93e636

Paste that token into the IDE to pair this browser with this binary.
Nothing leaves this machine: the browser connects to you, not the other way round.
The token is not stored; restarting invalidates it.
```

The threat model is narrow and worth stating exactly. The listener is bound to
`127.0.0.1`, so a remote host cannot reach it. What *can* reach it is any page
the user has open, because a browser will happily attempt requests to
localhost. Four things address that:

- the token is 32 bytes from the OS CSPRNG, never written to disk, and
  compared in **constant time** — a local page cannot recover it by timing;
- `Origin` is checked on the WebSocket upgrade, so a page from a remote site
  gets `403` even holding a valid token;
- CORS on `/health` returns `access-control-allow-origin` only for local
  origins, so a remote page cannot even detect that a binary is running;
- the protocol version is compared, not negotiated: a stale browser tab
  talking to a rebuilt binary is refused with both version numbers named.

## Two front halves, one set of diagnostics

The editor needs to mark errors without a round trip, so `web/src/languages/mekaneck/`
reimplements lex/parse/typecheck in TypeScript. Two front halves drift, and a
diagnostic that differs between the editor and the binary is worse than no
editor diagnostic at all — so both are pinned to one file of cases the Rust
generates:

```bash
cargo test -p mekaneck-lang --test fixtures -- --ignored   # regenerate
cargo test -p mekaneck-lang --test fixtures                # Rust side
cd web && npm test                                          # TypeScript side
```

`fixtures.json` holds 15 cases with exact line and column positions, each
carrying the rationale for why it exists, so a failure explains itself without
cross-referencing the papers. The suite has real discriminating power: changing
`MIN_COHERENCE` from 3 to 2 in the TypeScript alone immediately fails
`two_catalysts` while leaving the other fourteen green.

The mirror is not authoritative. It is fast and local; the binary re-checks on
`run`.

## No hand-written protocol types

`web/src/connection/protocol.ts` is **generated** from
`crates/server/src/protocol.rs` by `ts-rs`:

```bash
cargo test -p mekaneck-server export_bindings
```

A mismatched message shape fails at runtime over a socket, which is a worse
failure than a compile error — so the Rust is the single source of truth and
`crates/server/tests/bindings_are_current.rs` fails the build if the checked-in
TypeScript goes stale. It also asserts the two properties a client must not
lose in translation: that `Outcome::Declined` carries a *list* of cells, and
that `LawRow` carries `evidential`.

## Layout

```
chatelier/
├── Cargo.toml            workspace root
├── crates/
│   ├── algebra/          residual, power, compose, cascade, diagnose
│   ├── kernel/           node, graph, exec, schedule, trajectory
│   ├── lang/             lex, parse, types, eval, ast
│   ├── substrates/       the four obligations as a trait + bindings
│   ├── server/           loopback HTTP/WS, token, generated TS bindings
│   └── cli/              the `mekaneck` binary
├── web/src/
│   ├── connection/       generated protocol.ts + WebSocket client
│   └── languages/mekaneck/  lexer, parser, checker, Monaco defs, fixtures
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
cargo test                                   # Rust, 157 tests
cd web && npm test                           # TypeScript, 40 tests
python validation/run_all.py                 # Python, 21 checks

mekaneck serve --port 8731                   # then, against the live binary:
python validation/smoke_server.py --token <TOKEN>   # 19 end-to-end checks
```

Or, with `make`:

```bash
make check          # lint + all three suites + generated-artefact freshness
make generated      # regenerate bindings and fixtures, fail if they changed
```

The kernel's conformance suite additionally pins the inertia counts (5 chunks,
2 errors, 3 normal), the convergence result (1 protocol over 6 merge orders,
4 chunks on the shared identity), and the scheduler numbers (12 executions,
record 36, late chunk served in one step).

## Next

- The Next.js IDE shell: Monaco wired to `languages/mekaneck/monarch.ts`,
  a panel for diagnostics, a results view that renders a declination as a
  plurality rather than a choice, and a trajectory graph.
- A `kernel` binding for the server, so a run's committed record and
  read-to-emit relation stream to the browser as they happen.

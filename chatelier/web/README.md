# Web interface

A browser front end for the local `mekaneck` binary. The binary does the work;
this displays it.

```bash
npm install
npm test            # 40 tests
npm run typecheck
```

## What the interface is constrained not to do

Three results in the papers are easy to lose in a user interface, and losing
any of them turns a correct computation into a misleading display. Each is
tested in `src/components/semantics.test.tsx`, and each test has been checked
to fail when the constraint is violated.

**An algebraic identity is never presented as a finding.** A law row computed
under instance-specific estimation reports a perfect fit on data from any
process whatsoever. `LawComparison` segregates these into a separate band,
labels them, states why, and excludes them from best-fit ranking. They are not
hidden — an r of 1.000 marked as an identity is more instructive than an
absence — but they cannot be read as evidence.

**A contested closure is shown as a plurality, not a choice.** When a `seek`
declines, every reached cell is displayed with the catalysts that reached it.
Selecting one to display would assert a discrimination the evidence does not
license. A declination is styled distinctly from a failure, because it is a
normal termination.

**A floor carries its falsifiability.** An estimate from an estimator bounded
below by its own sample is drawn hatched, with the reason given: that estimator
returns a positive value on every input, including a process with no floor, so
its positivity is not evidence for a positive floor.

A fourth constraint concerns reading: when type separation falls below the
flagging threshold, `SeparationGauge` states that a non-trivial correlation may
still appear — carried by cascade-length variation rather than type identity —
and is not evidence that the typing is correct.

## Layout

```
src/
├── connection/
│   ├── protocol.ts       GENERATED from crates/server/src/protocol.rs
│   └── socket.ts         WebSocket client, request/response correlation
├── languages/mekaneck/
│   ├── lexer.ts          mirror of crates/lang/src/lex.rs
│   ├── parser.ts         mirror of crates/lang/src/parse.rs
│   ├── checker.ts        mirror of crates/lang/src/types.rs
│   ├── monarch.ts        Monaco language definition
│   └── fixtures.json     GENERATED shared diagnostic cases
├── components/
│   ├── charts/           LawComparison, FloorPanel, SeparationGauge
│   ├── panels/           OutcomePanel
│   └── shell/            App, Editor
├── state/store.ts        results as received, without interpretation
└── theme.ts              colour as semantics
```

## Two generated files

Neither is hand-edited. Both have tests that fail when they go stale.

```bash
cargo test -p mekaneck-server export_bindings              # protocol.ts
cargo test -p mekaneck-lang --test fixtures -- --ignored   # fixtures.json
```

`protocol.ts` exists because a mismatched message shape fails at runtime over a
socket, where it is expensive. `fixtures.json` exists because the editor
reimplements the compiler front half for instant diagnostics, and a diagnostic
that differs between editor and binary is worse than no editor diagnostic at
all.

The local checker is fast, not authoritative. The binary re-checks on run.

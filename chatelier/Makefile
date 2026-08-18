# Mekaneck — build, test, and the generation steps that prevent drift.
#
# Three implementations must agree: the Rust binary, the generated TypeScript
# protocol types, and the TypeScript mirror of the compiler front half. Two of
# those agreements are enforced by generated artefacts that are checked in, so
# `make check` fails if either goes stale.

.PHONY: all check test test-rust test-web test-python fmt lint bindings fixtures generated clean serve

all: check

# Everything that must pass before a commit.
check: lint test-rust test-web test-python generated

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

test: test-rust test-web test-python

test-rust:
	cargo test

test-web:
	cd web && npm test

test-python:
	cd validation && python run_all.py

# Requires a running binary; prints the token it needs.
#   make serve            (in one shell)
#   make test-server TOKEN=<token>
.PHONY: test-server
test-server:
	@test -n "$(TOKEN)" || (echo "usage: make test-server TOKEN=<token>" && exit 1)
	python validation/smoke_server.py --token $(TOKEN)

# ---------------------------------------------------------------------------
# Generated artefacts
# ---------------------------------------------------------------------------

# Regenerate both, then verify nothing changed. A diff here means someone
# altered a shared surface without re-exporting.
generated: bindings fixtures
	@git diff --quiet -- web/src/connection/protocol.ts \
	  web/src/languages/mekaneck/fixtures.json \
	  || (echo "" && \
	      echo "ERROR: generated files are stale. The diff above is what changed;" && \
	      echo "commit it, or revert the source change that caused it." && \
	      exit 1)
	@echo "generated artefacts are current"

# TypeScript protocol types, from crates/server/src/protocol.rs.
bindings:
	cargo test -p mekaneck-server export_bindings

# Shared diagnostic fixtures, from the Rust checker.
fixtures:
	cargo test -p mekaneck-lang --test fixtures -- --ignored

# ---------------------------------------------------------------------------
# Lint and format
# ---------------------------------------------------------------------------

lint:
	cargo clippy --all-targets -- -D warnings
	cd web && npx tsc --noEmit

fmt:
	cargo fmt

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

serve:
	cargo run -p mekaneck-cli -- serve

clean:
	cargo clean
	rm -rf web/node_modules

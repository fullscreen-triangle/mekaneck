"""
End-to-end smoke test of the loopback server.

Exercises the handshake (accept and both refusals) and every request type
against a live binary, using the generated protocol shapes. Run with the
server already listening:

    mekaneck serve --port 8731
    python validation/smoke_server.py --token <TOKEN>
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

import websockets

PROTOCOL = 1
GOOD_PROGRAM = """
substrate Osc { receivers : r(); observable : o(); events : e(); floor : asymptotic(); }
catalyst a : f() independent b, c;
catalyst b : g() independent a, c;
catalyst c : h() independent a, b;
let x = seek t() excluding rest() via (a, b, c) until closure;
report x;
"""

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))


async def send(ws, msg: dict) -> dict:
    await ws.send(json.dumps(msg))
    return json.loads(await ws.recv())


async def open_session(url: str, token: str, protocol: int = PROTOCOL):
    ws = await websockets.connect(url)
    reply = await send(ws, {"type": "hello", "token": token, "protocol": protocol})
    return ws, reply


async def main(url: str, token: str) -> int:
    # ---- handshake refusals -------------------------------------------
    _, denied = await open_session(url, "not-the-token")
    check("wrong token is denied", denied.get("type") == "denied",
          denied.get("reason", ""))
    check("denial does not echo the real token",
          token not in json.dumps(denied))

    _, stale = await open_session(url, token, protocol=PROTOCOL + 7)
    check("protocol mismatch is denied", stale.get("type") == "denied",
          stale.get("reason", "")[:60])

    ws = await websockets.connect(url)
    first = await send(ws, {"type": "ping", "request_id": "p0"})
    check("non-hello first frame is denied", first.get("type") == "denied")
    await ws.close()

    # ---- accepted session ---------------------------------------------
    ws, welcome = await open_session(url, token)
    check("valid token is accepted", welcome.get("type") == "welcome")
    check("welcome states where it is bound",
          welcome.get("bound_to", "").startswith("127.0.0.1"),
          welcome.get("bound_to", ""))

    # ping
    pong = await send(ws, {"type": "ping", "request_id": "p1"})
    check("ping is answered",
          pong.get("type") == "pong" and pong.get("request_id") == "p1")

    # check: clean program
    r = await send(ws, {
        "type": "check", "request_id": "c1", "source": GOOD_PROGRAM,
        "floors": [{"substrate": "Osc", "value": 12.5}],
    })
    check("clean program has no diagnostics",
          r.get("type") == "diagnostics" and not r.get("diagnostics"))

    # check: missing exclusion clause
    r = await send(ws, {
        "type": "check", "request_id": "c2",
        "source": GOOD_PROGRAM.replace("excluding rest() ", ""),
        "floors": [{"substrate": "Osc", "value": 12.5}],
    })
    d = (r.get("diagnostics") or [{}])[0]
    check("missing exclusion is an error with a position",
          d.get("severity") == "error" and d.get("line", 0) >= 1
          and "excluding" in d.get("message", ""),
          f"line {d.get('line')}, col {d.get('column')}")

    # check: absent floor is a warning, not an error
    r = await send(ws, {
        "type": "check", "request_id": "c3", "source": GOOD_PROGRAM, "floors": [],
    })
    d = (r.get("diagnostics") or [{}])[0]
    check("absent floor warns rather than fails", d.get("severity") == "warning")

    # run: unanimous -> resolved
    cells = [{"catalyst": c, "cell": "X"} for c in ("a", "b", "c")]
    r = await send(ws, {
        "type": "run", "request_id": "r1", "source": GOOD_PROGRAM,
        "floors": [{"substrate": "Osc", "value": 12.5}], "cells": cells,
    })
    b = (r.get("bindings") or [{}])[0]
    check("unanimous evidence resolves",
          r.get("type") == "run_result"
          and b.get("outcome", {}).get("outcome") == "resolved",
          f"record {b.get('record')}")

    # run: split -> declined, and NOT a failure frame
    cells = [{"catalyst": "a", "cell": "X"}, {"catalyst": "b", "cell": "X"},
             {"catalyst": "c", "cell": "Y"}]
    r = await send(ws, {
        "type": "run", "request_id": "r2", "source": GOOD_PROGRAM,
        "floors": [{"substrate": "Osc", "value": 12.5}], "cells": cells,
    })
    b = (r.get("bindings") or [{}])[0]
    out = b.get("outcome", {})
    check("split evidence declines as a RESULT, not a failure",
          r.get("type") == "run_result" and out.get("outcome") == "declined"
          and len(out.get("cells", [])) == 2,
          f"cells {out.get('cells')}")

    # analyse: both estimation regimes reported
    with open("examples/data/sleep_substrate.json", encoding="utf-8") as f:
        substrate = json.load(f)
    r = await send(ws, {
        "type": "analyse", "request_id": "a1", "substrate": substrate,
    })
    laws = r.get("laws", [])
    inst = [l for l in laws if l["estimation"] == "instance_specific"]
    typed = [l for l in laws if l["estimation"] == "type_averaged"]
    mult_inst = next((l for l in inst if l["law"] == "multiplicative"), {})
    mult_typed = next((l for l in typed if l["law"] == "multiplicative"), {})

    check("analysis returns both regimes",
          r.get("type") == "analysis_result" and len(inst) == 4 and len(typed) == 4,
          f"{r.get('cascades')} cascades, eta {r.get('separation', {}).get('eta', 0):.4f}")
    check("instance-specific rows are marked non-evidential",
          all(not l["evidential"] for l in inst))
    check("the telescoping identity holds on the wire",
          mult_inst.get("max_discrepancy", 1) < 1e-12,
          f"max dev {mult_inst.get('max_discrepancy'):.2e}")
    check("type-averaged rows are evidential and non-degenerate",
          all(l["evidential"] for l in typed)
          and mult_typed.get("max_discrepancy", 0) > 1e-6,
          f"r={mult_typed.get('pearson_r'):.4f}")
    check("floors carry their falsifiability",
          all(rec["falsifiable"] for rec in r.get("receivers", [])))

    # malformed frame does not kill the session
    await ws.send("{not json")
    bad = json.loads(await ws.recv())
    check("malformed frame is reported, not fatal", bad.get("type") == "failed")
    pong = await send(ws, {"type": "ping", "request_id": "p2"})
    check("session survives a malformed frame", pong.get("type") == "pong")

    await ws.close()

    n_fail = sum(1 for _, ok, _ in results if not ok)
    print(f"\n{len(results) - n_fail}/{len(results)} passed")
    return 1 if n_fail else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True)
    ap.add_argument("--url", default="ws://127.0.0.1:8731/ws")
    a = ap.parse_args()
    sys.exit(asyncio.run(main(a.url, a.token)))

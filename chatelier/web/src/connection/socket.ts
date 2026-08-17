/**
 * WebSocket client for the local `mekaneck` binary.
 *
 * The message types in `./protocol.ts` are GENERATED from `crates/server/src/
 * protocol.rs`. Do not edit them, and do not hand-write parallel interfaces
 * here: a mismatched shape fails at runtime over a socket, which is why the
 * Rust is the single source of truth.
 *
 * The browser connects *to* the user's machine. Nothing is uploaded, and the
 * token is a per-run pairing secret rather than an account credential —
 * restarting the binary invalidates it.
 */

import type { ClientMessage, ServerMessage } from "./protocol";

/** Must match `PROTOCOL_VERSION` in protocol.rs; the server refuses a mismatch. */
export const PROTOCOL_VERSION = 1;

export type ConnectionState =
  | { status: "idle" }
  | { status: "connecting" }
  | { status: "ready"; serverVersion: string; boundTo: string }
  | { status: "denied"; reason: string }
  | { status: "closed"; reason: string };

type Pending = {
  resolve: (msg: ServerMessage) => void;
  reject: (err: Error) => void;
  timer: ReturnType<typeof setTimeout>;
};

export interface ClientOptions {
  url?: string;
  token: string;
  /** How long to wait for a reply before rejecting. */
  timeoutMs?: number;
  onState?: (state: ConnectionState) => void;
  /** Frames that are not replies to a request, if any are added later. */
  onUnsolicited?: (msg: ServerMessage) => void;
}

/**
 * A request/response client over one socket.
 *
 * Requests are correlated by `request_id`, so several may be in flight — the
 * editor typically has a `check` outstanding while a `run` is still going.
 */
export class MekaneckClient {
  private ws: WebSocket | null = null;
  private pending = new Map<string, Pending>();
  private seq = 0;
  private state: ConnectionState = { status: "idle" };

  constructor(private readonly opts: ClientOptions) {}

  get connectionState(): ConnectionState {
    return this.state;
  }

  private setState(s: ConnectionState) {
    this.state = s;
    this.opts.onState?.(s);
  }

  /** Open the socket and complete the handshake. Resolves once welcomed. */
  connect(): Promise<void> {
    const url = this.opts.url ?? "ws://127.0.0.1:8731/ws";
    this.setState({ status: "connecting" });

    return new Promise((resolve, reject) => {
      let settled = false;
      const ws = new WebSocket(url);
      this.ws = ws;

      ws.onopen = () => {
        // The handshake must be the first frame.
        ws.send(
          JSON.stringify({
            type: "hello",
            token: this.opts.token,
            protocol: PROTOCOL_VERSION,
          } satisfies ClientMessage),
        );
      };

      ws.onmessage = (ev) => {
        let msg: ServerMessage;
        try {
          msg = JSON.parse(ev.data as string) as ServerMessage;
        } catch {
          return; // a frame we cannot parse is not actionable
        }

        if (!settled) {
          settled = true;
          if (msg.type === "welcome") {
            this.setState({
              status: "ready",
              serverVersion: msg.server_version,
              boundTo: msg.bound_to,
            });
            resolve();
          } else if (msg.type === "denied") {
            this.setState({ status: "denied", reason: msg.reason });
            reject(new Error(msg.reason));
          } else {
            const reason = "server did not complete the handshake";
            this.setState({ status: "denied", reason });
            reject(new Error(reason));
          }
          return;
        }

        this.deliver(msg);
      };

      ws.onerror = () => {
        if (!settled) {
          settled = true;
          const reason = `cannot reach ${url} — is the binary running? try: mekaneck serve`;
          this.setState({ status: "closed", reason });
          reject(new Error(reason));
        }
      };

      ws.onclose = (ev) => {
        // Reject anything still outstanding rather than leaving it hanging.
        for (const [, p] of this.pending) {
          clearTimeout(p.timer);
          p.reject(new Error("connection closed"));
        }
        this.pending.clear();
        if (this.state.status !== "denied") {
          this.setState({
            status: "closed",
            reason: ev.reason || "connection closed",
          });
        }
      };
    });
  }

  private deliver(msg: ServerMessage) {
    const id =
      "request_id" in msg && typeof msg.request_id === "string"
        ? msg.request_id
        : "";
    const p = id ? this.pending.get(id) : undefined;
    if (!p) {
      this.opts.onUnsolicited?.(msg);
      return;
    }
    clearTimeout(p.timer);
    this.pending.delete(id);
    p.resolve(msg);
  }

  private request(
    build: (requestId: string) => ClientMessage,
  ): Promise<ServerMessage> {
    if (!this.ws || this.state.status !== "ready") {
      return Promise.reject(new Error("not connected"));
    }
    const id = `r${++this.seq}`;
    const ws = this.ws;

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`request ${id} timed out`));
      }, this.opts.timeoutMs ?? 30_000);

      this.pending.set(id, { resolve, reject, timer });
      ws.send(JSON.stringify(build(id)));
    });
  }

  /** Parse and type-check. Cheap enough for keystroke-driven use. */
  async check(
    source: string,
    floors: Array<{ substrate: string; value: number }> = [],
  ) {
    const msg = await this.request((request_id) => ({
      type: "check",
      request_id,
      source,
      floors,
    }));
    if (msg.type === "diagnostics") return msg.diagnostics;
    if (msg.type === "failed") throw new Error(msg.message);
    throw new Error(`unexpected reply ${msg.type}`);
  }

  /**
   * Evaluate the program's `seek` bindings.
   *
   * A binding whose outcome is `declined` is a normal result carrying several
   * incompatible cells — render the plurality; do not pick one.
   */
  async run(
    source: string,
    floors: Array<{ substrate: string; value: number }>,
    cells: Array<{ catalyst: string; cell: string }>,
  ) {
    const msg = await this.request((request_id) => ({
      type: "run",
      request_id,
      source,
      floors,
      cells,
    }));
    if (msg.type === "run_result") return msg.bindings;
    if (msg.type === "failed") throw new Error(msg.message);
    throw new Error(`unexpected reply ${msg.type}`);
  }

  /**
   * Analyse a substrate.
   *
   * The returned `laws` contain rows from both estimation regimes. Rows with
   * `evidential === false` are algebraic identities: they report a perfect fit
   * on data from any process whatsoever, so a UI must not present them as
   * findings.
   */
  async analyse(substrate: unknown) {
    const msg = await this.request((request_id) => ({
      type: "analyse",
      request_id,
      substrate,
    }));
    if (msg.type === "analysis_result") return msg;
    if (msg.type === "failed") throw new Error(msg.message);
    throw new Error(`unexpected reply ${msg.type}`);
  }

  async ping() {
    const msg = await this.request((request_id) => ({
      type: "ping",
      request_id,
    }));
    return msg.type === "pong";
  }

  close() {
    this.ws?.close();
    this.ws = null;
  }
}

/** Probe for a running binary before prompting for a token. */
export async function probe(
  origin = "http://127.0.0.1:8731",
): Promise<{ running: boolean; version?: string; protocol?: number }> {
  try {
    const res = await fetch(`${origin}/health`, { mode: "cors" });
    if (!res.ok) return { running: false };
    const body = (await res.json()) as { version: string; protocol: number };
    return { running: true, version: body.version, protocol: body.protocol };
  } catch {
    return { running: false };
  }
}

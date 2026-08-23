/**
 * Pairing with a local binary.
 *
 * The binary does the work and this displays it, so the token exchange is the
 * point at which the tool becomes usable rather than a detail of setup. It is
 * given its own panel for that reason.
 *
 * One case is reported rather than attempted. A page served over https cannot
 * open `ws://127.0.0.1`: the browser refuses it as mixed content before the
 * binary is contacted, and no token can change that. Offering a token field
 * there would send the reader after a fault that is not theirs, so the panel
 * explains the situation and gives the two commands that do work.
 */

import { useState } from "react";

import { mono, palette, sans } from "../../theme";
import { useStore } from "../../state/store";

const DEFAULT_URL = "ws://127.0.0.1:8731/ws";

/**
 * Whether this origin may open a loopback websocket at all.
 *
 * Mixed content is blocked for https pages only; an http page served from
 * localhost during development pairs normally, which is the intended path.
 */
export function canPairFromHere(): boolean {
  if (typeof window === "undefined") return true;
  return window.location.protocol !== "https:";
}

export function Pairing() {
  const { connection, connect, disconnect } = useStore();
  const [token, setToken] = useState("");
  const [url, setUrl] = useState(DEFAULT_URL);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!canPairFromHere()) return <HostedNotice />;

  if (connection.status === "ready") {
    return (
      <div style={{ fontFamily: mono, fontSize: 11 }}>
        <Row label="status" value="paired" colour={palette.resolved} />
        <Row label="server" value={connection.serverVersion} />
        <Row label="bound to" value={connection.boundTo} />
        <p style={note}>
          Analysis runs in the binary on this machine. Nothing is sent anywhere
          else.
        </p>
        <button onClick={disconnect} style={btn(palette.bgElevated, palette.text)}>
          Disconnect
        </button>
      </div>
    );
  }

  const submit = async () => {
    setError(null);
    setBusy(true);
    try {
      await connect(token.trim(), url.trim() || DEFAULT_URL);
    } catch (e) {
      // A refused pairing is an ordinary outcome, not a crash: a stale token,
      // a binary that is not running, a port already taken.
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ fontFamily: sans, fontSize: 12 }}>
      <p style={note}>Start the binary on this machine, then paste the token it prints.</p>

      <pre style={pre}>mekaneck serve --port 8731</pre>

      <label style={lbl}>Token</label>
      <input
        value={token}
        onChange={(e) => setToken(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && token.trim() && !busy) void submit();
        }}
        placeholder="paste the token from the terminal"
        spellCheck={false}
        autoComplete="off"
        style={input}
      />

      <label style={lbl}>Address</label>
      <input
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        spellCheck={false}
        autoComplete="off"
        style={input}
      />

      <button
        onClick={() => void submit()}
        disabled={busy || token.trim().length === 0}
        style={btn(
          token.trim() && !busy ? palette.accent : palette.bgElevated,
          token.trim() && !busy ? "#fff" : palette.textFaint,
        )}
      >
        {busy ? "Pairing…" : "Pair"}
      </button>

      {(error || connection.status === "denied") && (
        <div style={{ ...note, color: palette.failed, marginTop: 10 }}>
          {error ?? (connection.status === "denied" ? connection.reason : "")}
        </div>
      )}

      <p style={{ ...note, marginTop: 14, color: palette.textFaint }}>
        The token is a per-run pairing secret, not an account credential: 32
        bytes from the operating system CSPRNG, never written to disk, and
        invalidated when the binary restarts.
      </p>
    </div>
  );
}

/**
 * What a hosted instance can and cannot do.
 *
 * Stated as a property of the browser rather than as a limitation of the
 * tool, because that is what it is — and because the paired workflow is fully
 * available one command away.
 */
function HostedNotice() {
  return (
    <div style={{ fontFamily: sans, fontSize: 12 }}>
      <div
        style={{
          padding: "9px 11px",
          marginBottom: 12,
          borderLeft: `2px solid ${palette.warn}`,
          background: palette.bgSunken,
          fontSize: 11,
          lineHeight: 1.6,
          color: palette.textDim,
        }}
      >
        This page is served over https, and a browser will not open a{" "}
        <code style={{ fontFamily: mono }}>ws://</code> connection to{" "}
        <code style={{ fontFamily: mono }}>127.0.0.1</code> from an https
        origin — it is blocked as mixed content before your binary is
        contacted. That restriction is the same-origin rule doing what the
        local-only guarantee claims, so it is reported rather than worked
        around.
      </div>

      <p style={note}>
        Run the tool locally to pair. Both commands take a few seconds:
      </p>

      <pre style={pre}>{`git clone https://github.com/fullscreen-triangle/mekaneck
cd mekaneck/chatelier

cargo run --release --bin mekaneck -- serve --port 8731
cd web && npm install && npm run dev`}</pre>

      <p style={{ ...note, color: palette.textFaint }}>
        The editor at <code style={{ fontFamily: mono }}>127.0.0.1:5173</code>{" "}
        is served over http, so it pairs with the binary normally. Everything
        on this hosted page — the paper, the charts, the cardiac record — is
        the same there.
      </p>
    </div>
  );
}

/* ------------------------------- bits ------------------------------ */

const note: React.CSSProperties = {
  fontSize: 11,
  lineHeight: 1.6,
  color: palette.textDim,
  margin: "0 0 10px",
};

const pre: React.CSSProperties = {
  fontFamily: mono,
  fontSize: 10.5,
  lineHeight: 1.65,
  color: palette.text,
  background: palette.bgSunken,
  border: `1px solid ${palette.borderSubtle}`,
  borderRadius: 3,
  padding: "9px 11px",
  margin: "0 0 12px",
  overflowX: "auto",
  whiteSpace: "pre",
};

const lbl: React.CSSProperties = {
  display: "block",
  fontFamily: mono,
  fontSize: 9.5,
  letterSpacing: "0.08em",
  textTransform: "uppercase",
  color: palette.textFaint,
  margin: "0 0 4px",
};

const input: React.CSSProperties = {
  width: "100%",
  boxSizing: "border-box",
  padding: "6px 8px",
  marginBottom: 10,
  background: palette.bgSunken,
  border: `1px solid ${palette.border}`,
  borderRadius: 3,
  color: palette.text,
  fontFamily: mono,
  fontSize: 11,
  outline: "none",
};

function btn(bg: string, fg: string): React.CSSProperties {
  return {
    padding: "6px 14px",
    background: bg,
    border: "none",
    borderRadius: 3,
    color: fg,
    fontFamily: sans,
    fontSize: 12,
    cursor: bg === palette.bgElevated ? "default" : "pointer",
  };
}

function Row({ label, value, colour = palette.text }: { label: string; value: string; colour?: string }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        padding: "3px 4px",
        borderBottom: `1px solid ${palette.borderSubtle}`,
      }}
    >
      <span style={{ color: palette.textDim }}>{label}</span>
      <span style={{ color: colour }}>{value}</span>
    </div>
  );
}

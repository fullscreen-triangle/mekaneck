//! The loopback token.
//!
//! The threat model is narrow and worth stating exactly, because it determines
//! how much this code needs to do.
//!
//! The server binds to `127.0.0.1` only, so a remote host cannot reach it. What
//! *can* reach it is any process on the same machine, and — more importantly —
//! any web page the user happens to have open, because a page from any origin
//! may attempt requests to localhost. The token exists to stop that: a page
//! that does not know it cannot drive the user's analysis binary.
//!
//! Three consequences follow, all implemented here:
//!
//! - the token is generated per-run from the OS CSPRNG, never persisted, and
//!   printed once on startup;
//! - comparison is constant-time, so a page cannot recover it by timing;
//! - `Origin` is checked on the WebSocket upgrade, because a browser will send
//!   one and a same-origin page is the only legitimate caller.

use std::fmt;

use subtle::ConstantTimeEq;

/// A per-run secret pairing one browser session to this binary.
#[derive(Clone)]
pub struct Token(String);

impl Token {
    /// Generate 32 bytes from the OS CSPRNG, hex-encoded.
    ///
    /// Not persisted anywhere: restarting the binary invalidates every open
    /// session, which is the behaviour we want — a token that outlived the
    /// process would be a credential, and this is not one.
    pub fn generate() -> Result<Self, Error> {
        let mut bytes = [0u8; 32];
        getrandom::fill(&mut bytes).map_err(|e| Error::Entropy(e.to_string()))?;
        Ok(Token(
            bytes.iter().map(|b| format!("{b:02x}")).collect::<String>(),
        ))
    }

    /// Constant-time equality.
    ///
    /// `String == String` short-circuits on the first differing byte, which
    /// leaks the length of a correct prefix to a caller that can time it. A
    /// local page can time it very precisely.
    pub fn matches(&self, candidate: &str) -> bool {
        let a = self.0.as_bytes();
        let b = candidate.as_bytes();
        if a.len() != b.len() {
            // Length is not secret — it is a compile-time constant — so an
            // early return here reveals nothing.
            return false;
        }
        a.ct_eq(b).into()
    }

    /// The value to print on startup and paste into the browser.
    pub fn expose(&self) -> &str {
        &self.0
    }
}

/// Never print a token by accident in a log line or a panic message.
impl fmt::Debug for Token {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Token(<redacted>)")
    }
}

/// Whether an `Origin` header may drive this server.
///
/// A WebSocket upgrade from a browser always carries `Origin`; a non-browser
/// client may omit it. We accept a missing header (that is `curl`, or the CLI
/// itself) and otherwise require a loopback origin, so a page served from a
/// remote site cannot use a leaked token from the user's browser.
pub fn origin_is_local(origin: Option<&str>) -> bool {
    let Some(origin) = origin else {
        return true;
    };
    // Accept the forms a local dev server or packaged app actually produces.
    for prefix in [
        "http://localhost",
        "https://localhost",
        "http://127.0.0.1",
        "https://127.0.0.1",
        "http://[::1]",
        "https://[::1]",
        // Tauri / packaged shells
        "tauri://localhost",
        "file://",
    ] {
        if origin == prefix || origin.starts_with(&format!("{prefix}:")) {
            return true;
        }
    }
    false
}

#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("could not obtain entropy for a token: {0}")]
    Entropy(String),
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tokens_are_long_and_distinct() {
        let a = Token::generate().unwrap();
        let b = Token::generate().unwrap();
        assert_eq!(a.expose().len(), 64);
        assert_ne!(a.expose(), b.expose());
    }

    #[test]
    fn matching_accepts_only_the_exact_token() {
        let t = Token::generate().unwrap();
        assert!(t.matches(t.expose()));
        assert!(!t.matches(""));
        assert!(!t.matches("wrong"));

        // a correct prefix must not be accepted
        let mut prefix = t.expose().to_string();
        prefix.pop();
        assert!(!t.matches(&prefix));

        // same length, one byte different
        let mut altered: Vec<u8> = t.expose().bytes().collect();
        altered[0] = if altered[0] == b'a' { b'b' } else { b'a' };
        assert!(!t.matches(std::str::from_utf8(&altered).unwrap()));
    }

    #[test]
    fn debug_never_reveals_the_token() {
        let t = Token::generate().unwrap();
        let shown = format!("{t:?}");
        assert!(!shown.contains(t.expose()));
        assert!(shown.contains("redacted"));
    }

    #[test]
    fn local_origins_are_accepted_and_remote_ones_are_not() {
        for ok in [
            None,
            Some("http://localhost:3000"),
            Some("http://127.0.0.1:8731"),
            Some("https://localhost"),
            Some("tauri://localhost"),
        ] {
            assert!(origin_is_local(ok), "should accept {ok:?}");
        }
        for bad in [
            Some("https://evil.example"),
            Some("http://localhost.evil.example"),
            Some("http://notlocalhost"),
            Some("https://127.0.0.1.evil.example"),
        ] {
            assert!(!origin_is_local(bad), "should reject {bad:?}");
        }
    }
}

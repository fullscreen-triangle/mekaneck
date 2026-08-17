//! WebSocket transport: framing, handshake, dispatch. No analysis logic.
//!
//! The handshake is strict on purpose. A socket must send [`ClientMessage::Hello`]
//! as its first frame, carrying a matching token and an exact protocol version;
//! anything else is refused and the socket closed. A stale browser tab talking
//! to a rebuilt binary is precisely the drift this project treats as a bug, so
//! versions are compared rather than negotiated.

use std::sync::Arc;

use axum::extract::ws::{Message, WebSocket};

use crate::auth::Token;
use crate::handlers;
use crate::protocol::{ClientMessage, ServerMessage, PROTOCOL_VERSION};

/// State shared by all connections.
#[derive(Debug)]
pub struct AppState {
    pub token: Token,
    pub bound_to: String,
    pub version: String,
}

impl AppState {
    pub fn new(token: Token, bound_to: impl Into<String>) -> Self {
        AppState {
            token,
            bound_to: bound_to.into(),
            version: env!("CARGO_PKG_VERSION").to_string(),
        }
    }
}

/// Outcome of inspecting the first frame.
#[derive(Debug, PartialEq)]
pub enum Handshake {
    Accepted,
    Denied(String),
}

/// Validate the opening frame.
///
/// Separated from the socket so it can be tested directly — the handshake is
/// the security boundary, and it should not require a network to exercise.
pub fn handshake(state: &AppState, first_frame: &str) -> Handshake {
    let msg: ClientMessage = match serde_json::from_str(first_frame) {
        Ok(m) => m,
        Err(e) => return Handshake::Denied(format!("unparseable hello: {e}")),
    };
    match msg {
        ClientMessage::Hello { token, protocol } => {
            if protocol != PROTOCOL_VERSION {
                // Say both numbers: the usual cause is a cached page.
                return Handshake::Denied(format!(
                    "protocol {protocol} but this binary speaks {PROTOCOL_VERSION}; \
                     reload the page to pick up the matching client"
                ));
            }
            if !state.token.matches(&token) {
                return Handshake::Denied("token does not match this binary".into());
            }
            Handshake::Accepted
        }
        _ => Handshake::Denied("first frame must be hello".into()),
    }
}

/// Drive one connection to completion.
pub async fn serve(mut socket: WebSocket, state: Arc<AppState>) {
    // --- handshake -------------------------------------------------------
    let first = match socket.recv().await {
        Some(Ok(Message::Text(t))) => t.to_string(),
        _ => return, // closed, binary, or errored before saying hello
    };

    match handshake(&state, &first) {
        Handshake::Denied(reason) => {
            let _ = send(&mut socket, &ServerMessage::Denied { reason }).await;
            // Closing is best-effort: the peer may already be gone, and a
            // failure here has nothing left to report to.
            let _ = socket.send(Message::Close(None)).await;
            return;
        }
        Handshake::Accepted => {
            let welcome = ServerMessage::Welcome {
                protocol: PROTOCOL_VERSION,
                server_version: state.version.clone(),
                bound_to: state.bound_to.clone(),
            };
            if send(&mut socket, &welcome).await.is_err() {
                return;
            }
        }
    }

    // --- request loop ----------------------------------------------------
    while let Some(frame) = socket.recv().await {
        let text = match frame {
            Ok(Message::Text(t)) => t.to_string(),
            Ok(Message::Close(_)) | Err(_) => break,
            // Ping/Pong are handled by the transport; binary is not used.
            Ok(_) => continue,
        };

        let reply = match serde_json::from_str::<ClientMessage>(&text) {
            Ok(msg) => handlers::dispatch(msg),
            Err(e) => ServerMessage::Failed {
                request_id: String::new(),
                message: format!("unparseable message: {e}"),
            },
        };

        if send(&mut socket, &reply).await.is_err() {
            break;
        }
    }
}

async fn send(socket: &mut WebSocket, msg: &ServerMessage) -> Result<(), axum::Error> {
    let text = serde_json::to_string(msg).map_err(axum::Error::new)?;
    socket.send(Message::Text(text.into())).await
}

#[cfg(test)]
mod tests {
    use super::*;

    fn state() -> AppState {
        AppState::new(Token::generate().unwrap(), "127.0.0.1:8731")
    }

    fn hello(token: &str, protocol: u32) -> String {
        serde_json::to_string(&ClientMessage::Hello {
            token: token.into(),
            protocol,
        })
        .unwrap()
    }

    #[test]
    fn a_matching_hello_is_accepted() {
        let s = state();
        let frame = hello(s.token.expose(), PROTOCOL_VERSION);
        assert_eq!(handshake(&s, &frame), Handshake::Accepted);
    }

    #[test]
    fn a_wrong_token_is_denied() {
        let s = state();
        let frame = hello("not-the-token", PROTOCOL_VERSION);
        match handshake(&s, &frame) {
            Handshake::Denied(r) => assert!(r.contains("token")),
            other => panic!("expected denial, got {other:?}"),
        }
    }

    #[test]
    fn a_version_mismatch_names_both_versions() {
        let s = state();
        let frame = hello(s.token.expose(), PROTOCOL_VERSION + 7);
        match handshake(&s, &frame) {
            Handshake::Denied(r) => {
                assert!(r.contains(&(PROTOCOL_VERSION + 7).to_string()));
                assert!(r.contains(&PROTOCOL_VERSION.to_string()));
                assert!(r.contains("reload"));
            }
            other => panic!("expected denial, got {other:?}"),
        }
    }

    #[test]
    fn a_non_hello_first_frame_is_denied() {
        let s = state();
        let frame = serde_json::to_string(&ClientMessage::Ping {
            request_id: "p".into(),
        })
        .unwrap();
        match handshake(&s, &frame) {
            Handshake::Denied(r) => assert!(r.contains("first frame")),
            other => panic!("expected denial, got {other:?}"),
        }
    }

    #[test]
    fn garbage_is_denied_without_panicking() {
        let s = state();
        assert!(matches!(handshake(&s, "{not json"), Handshake::Denied(_)));
        assert!(matches!(handshake(&s, ""), Handshake::Denied(_)));
    }

    #[test]
    fn a_denial_never_echoes_the_expected_token() {
        let s = state();
        let frame = hello("guess", PROTOCOL_VERSION);
        if let Handshake::Denied(r) = handshake(&s, &frame) {
            assert!(!r.contains(s.token.expose()));
        }
    }
}

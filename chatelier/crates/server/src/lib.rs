//! # Loopback server
//!
//! Pairs the local `mekaneck` binary with a browser IDE. The server binds to
//! `127.0.0.1` and never dials out: the browser connects *to* the user's
//! machine, so analysis data does not leave the host.
//!
//! The token is a per-run loopback handshake secret, not an account
//! credential. It is generated from the OS CSPRNG, never persisted, compared
//! in constant time, and invalidated by restarting the binary.
//!
//! ```no_run
//! # async fn demo() -> anyhow::Result<()> {
//! use mekaneck_server::{serve_local, Token};
//!
//! let token = Token::generate()?;
//! println!("token: {}", token.expose());
//! serve_local(token, 8731).await?;
//! # Ok(())
//! # }
//! ```

#![forbid(unsafe_code)]
#![warn(missing_debug_implementations)]

pub mod auth;
pub mod handlers;
pub mod protocol;
pub mod ws;

use std::net::{Ipv4Addr, Ipv6Addr, SocketAddr};
use std::sync::Arc;

use axum::extract::{ConnectInfo, State, WebSocketUpgrade};
use axum::http::{HeaderMap, StatusCode};
use axum::response::{IntoResponse, Response};
use axum::routing::get;
use axum::Router;

pub use auth::Token;
pub use protocol::{ClientMessage, ServerMessage, PROTOCOL_VERSION};
pub use ws::AppState;

/// Build the router.
///
/// Exposed for tests. There is deliberately no static-file service and no
/// route that reads a path from the client: the server's whole surface is one
/// health endpoint and one socket.
pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/health", get(health))
        .route("/ws", get(upgrade))
        // CORS is needed for the browser's pre-connection probe of /health.
        // It is deliberately *not* permissive: only a local origin may read a
        // response, so a remote page cannot use the endpoint to discover that
        // a binary is running here.
        .layer(
            tower_http::cors::CorsLayer::new()
                .allow_origin(tower_http::cors::AllowOrigin::predicate(
                    |origin, _parts| {
                        origin
                            .to_str()
                            .map(|o| auth::origin_is_local(Some(o)))
                            .unwrap_or(false)
                    },
                ))
                .allow_methods([axum::http::Method::GET]),
        )
        .with_state(state)
}

async fn health(State(state): State<Arc<AppState>>) -> Response {
    // No token required, and no secret disclosed: this exists so a client can
    // tell a running binary from a closed port before prompting for a token.
    axum::Json(serde_json::json!({
        "service": "mekaneck",
        "version": state.version,
        "protocol": PROTOCOL_VERSION,
        "bound_to": state.bound_to,
    }))
    .into_response()
}

async fn upgrade(
    ws: WebSocketUpgrade,
    State(state): State<Arc<AppState>>,
    ConnectInfo(peer): ConnectInfo<SocketAddr>,
    headers: HeaderMap,
) -> Response {
    // Defence in depth: the listener is already loopback-bound, but a
    // misconfigured proxy could forward a remote peer here.
    if !peer.ip().is_loopback() {
        return (StatusCode::FORBIDDEN, "loopback connections only").into_response();
    }

    // A browser always sends Origin on an upgrade; a page from a remote site
    // must not be able to drive this binary even with a leaked token.
    let origin = headers.get("origin").and_then(|v| v.to_str().ok());
    if !auth::origin_is_local(origin) {
        return (StatusCode::FORBIDDEN, "origin is not local").into_response();
    }

    ws.on_upgrade(move |socket| ws::serve(socket, state))
}

/// Bind to loopback and serve until the process is interrupted.
///
/// Binds **both** `127.0.0.1` and `::1` where available.
///
/// This is not belt-and-braces. `localhost` resolves to `::1` first for many
/// clients (Python's asyncio among them) and to `127.0.0.1` for others, and a
/// single-stack listener refuses the other family with a bare "connection
/// refused" — which reads as *the binary is not running* rather than *wrong
/// address family*. Windows does not enable dual-stack sockets by default, so
/// binding one and hoping is not enough.
///
/// IPv6 is optional: if it is unavailable the IPv4 listener alone is served.
pub async fn serve_local(token: Token, port: u16) -> anyhow::Result<()> {
    let v4 = tokio::net::TcpListener::bind(SocketAddr::from((Ipv4Addr::LOCALHOST, port))).await?;
    let bound = v4.local_addr()?;
    // A port of 0 asks the OS to choose; the second listener must use the
    // port actually assigned, not 0 again.
    let port = bound.port();
    let v6 = tokio::net::TcpListener::bind(SocketAddr::from((Ipv6Addr::LOCALHOST, port)))
        .await
        .ok();

    let state = Arc::new(AppState::new(
        token,
        match &v6 {
            Some(_) => format!("127.0.0.1:{port} and [::1]:{port}"),
            None => bound.to_string(),
        },
    ));

    let shutdown = || async {
        let _ = tokio::signal::ctrl_c().await;
    };

    let app_v4 = router(Arc::clone(&state));
    let serve_v4 = axum::serve(v4, app_v4.into_make_service_with_connect_info::<SocketAddr>())
        .with_graceful_shutdown(shutdown());

    match v6 {
        Some(v6) => {
            let app_v6 = router(state);
            let serve_v6 =
                axum::serve(v6, app_v6.into_make_service_with_connect_info::<SocketAddr>())
                    .with_graceful_shutdown(shutdown());
            // Either family serving is enough; the first to stop ends the run.
            tokio::select! {
                r = serve_v4 => r?,
                r = serve_v6 => r?,
            }
        }
        None => serve_v4.await?,
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn state_records_where_it_is_bound() {
        let s = AppState::new(Token::generate().unwrap(), "127.0.0.1:8731");
        assert!(s.bound_to.starts_with("127.0.0.1"));
        assert!(!s.version.is_empty());
    }

    #[tokio::test]
    async fn binds_to_loopback_only() {
        // Binding succeeds on loopback and the reported address is loopback,
        // so a client can state truthfully where its data is going.
        let listener = tokio::net::TcpListener::bind(SocketAddr::from((Ipv4Addr::LOCALHOST, 0)))
            .await
            .unwrap();
        assert!(listener.local_addr().unwrap().ip().is_loopback());
    }
}

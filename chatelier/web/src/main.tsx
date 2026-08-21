/**
 * Browser entry point.
 *
 * The landing page is shown first and the editor is entered deliberately.
 * That ordering is the point: the editor will happily run a program over a
 * substrate whose floor obligation fails, and report a declination as a
 * normal termination. A reader who has not been told why neither of those is
 * an error will read both as the tool misbehaving.
 *
 * The route is kept in the URL hash so a reader can link to either view, and
 * so entering the editor does not lose the landing page from history.
 */

import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./components/shell/App";
import { Landing } from "./components/landing/Landing";

type Route = "landing" | "editor";

function routeFromHash(): Route {
  return window.location.hash.replace(/^#\/?/, "") === "editor" ? "editor" : "landing";
}

function Root() {
  const [route, setRoute] = useState<Route>(routeFromHash);

  useEffect(() => {
    const onHash = () => setRoute(routeFromHash());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  if (route === "editor") return <App />;
  return <Landing onEnter={() => { window.location.hash = "#/editor"; }} />;
}

const host = document.getElementById("root");
if (!host) throw new Error("no #root element");

createRoot(host).render(
  <StrictMode>
    <Root />
  </StrictMode>,
);

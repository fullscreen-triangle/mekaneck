import { useState, useEffect } from "react";

export function useThemeSwitch() {
  const [mode, setMode] = useState("dark");

  useEffect(() => {
    document.documentElement.classList.add("dark");
    window.localStorage.setItem("theme", "dark");
  }, []);

  return [mode, setMode];
}

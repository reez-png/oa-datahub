// pages/_app.tsx
import type { AppProps } from "next/app";
import { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";

function Header() {
  const [mounted, setMounted] = useState(false);
  const [authed, setAuthed] = useState(false);
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);

    const read = () => {
      const token = localStorage.getItem("sb-access-token");
      setAuthed(!!token);

      // fetch /me if we have a token
      const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      if (token) {
        fetch(`${API}/me`, { headers: { Authorization: `Bearer ${token}` } })
          .then((r) => (r.ok ? r.json() : null))
          .then((j) => setEmail(j?.email ?? null))
          .catch(() => setEmail(null));
      } else {
        setEmail(null);
      }
    };

    // initial read
    read();

    // keep auth state in sync across tabs
    const onStorage = (e: StorageEvent) => {
      if (e.key === "sb-access-token") read();
    };
    window.addEventListener("storage", onStorage);

    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const logout = () => {
    localStorage.removeItem("sb-access-token");
    // hard redirect avoids hydration edge cases
    window.location.href = "/login";
  };

  return (
    <div
      style={{
        padding: "8px 16px",
        borderBottom: "1px solid #eee",
        display: "flex",
        alignItems: "center",
        gap: 12,
      }}
    >
      <a href="/">Datasets</a>

      {!authed && (
        <a href="/login" style={{ marginLeft: "auto" }}>
          Login
        </a>
      )}

      {mounted && authed && (
        <>
          <span style={{ marginLeft: "auto" }}>{email || "Signed in"}</span>
          <button onClick={logout} style={{ marginLeft: 8 }}>
            Logout
          </button>
        </>
      )}

      {!mounted && <span style={{ marginLeft: "auto" }} />}
    </div>
  );
}

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Header />
      <Component {...pageProps} />
    </>
  );
}

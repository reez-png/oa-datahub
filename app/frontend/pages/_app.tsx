import type { AppProps } from "next/app";
import "leaflet/dist/leaflet.css";

function Header() {
  function logout() {
    localStorage.removeItem("sb-access-token");
    window.location.href = "/login";
  }
  const token =
    typeof window !== "undefined" ? localStorage.getItem("sb-access-token") : null;

  return (
    <div
      style={{
        padding: "8px 16px",
        borderBottom: "1px solid #eee",
        display: "flex",
        gap: 12,
        alignItems: "center",
      }}
    >
      <a href="/">Datasets</a>
      <a href="/login">Login</a>
      {token && (
        <button onClick={logout} style={{ marginLeft: "auto" }}>
          Logout
        </button>
      )}
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

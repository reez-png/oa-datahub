import { useEffect, useState } from "react";
import { authFetch } from "../lib/auth";

const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

type Dataset = {
  id: number;
  name: string;
  region: string;
  start_date: string;
  end_date: string;
  source: string;
};

export default function Home() {
  const [rows, setRows] = useState<Dataset[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const r = await authFetch(`${API}/datasets`);
        if (!r.ok) throw new Error(`Failed (${r.status})`);
        const json = await r.json();
        if (alive) setRows(json);
      } catch (e: any) {
        if (alive) setErr(String(e?.message ?? e));
        console.error(e);
      }
    })();
    return () => { alive = false; };
  }, []);

  return (
    <main style={{ padding: "16px", fontFamily: "Inter, system-ui, sans-serif" }}>
      <h1 style={{ marginBottom: 12 }}>Datasets</h1>
      {err && <p style={{ color: "#b00" }}>{err}</p>}
      <ul>
        {rows.map((d) => (
          <li key={d.id} style={{ marginBottom: 8 }}>
            <a href={`/datasets/${d.id}`} style={{ textDecoration: "underline" }}>
              {d.name}
            </a>{" "}
            <small>({d.region})</small>
          </li>
        ))}
      </ul>
      {rows.length === 0 && !err && (
        <p>No datasets yet. Create one in Swagger, then refresh.</p>
      )}
    </main>
  );
}

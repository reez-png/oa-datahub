import { useEffect, useState } from "react";

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
  useEffect(() => {
    fetch(`${API}/datasets`).then(r => r.json()).then(setRows).catch(console.error);
  }, []);
  return (
    <main style={{padding:"16px", fontFamily:"Inter, system-ui, sans-serif"}}>
      <h1 style={{marginBottom:12}}>Datasets</h1>
      <ul>
        {rows.map(d => (
          <li key={d.id} style={{marginBottom:8}}>
            <a href={`/datasets/${d.id}`} style={{textDecoration:"underline"}}>
              {d.name}
            </a>{" "}
            <small>({d.region})</small>
          </li>
        ))}
      </ul>
      {rows.length === 0 && <p>No datasets yet. Create one in Swagger, then refresh.</p>}
    </main>
  );
}

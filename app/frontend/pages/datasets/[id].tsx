import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { authFetch } from "../../lib/auth";

const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
const MapClient = dynamic(() => import("../../components/MapClient"), { ssr: false });

type Column = { name: string; dtype: string; non_null: number };
type PreviewOk = { columns: Column[]; data: Record<string, any>[]; stored_path: string; note?: string };
type PreviewErr = { detail?: string } & Record<string, any>;
type PreviewResp = PreviewOk | PreviewErr;

type FileRow = { file_id:number; stored_path:string; original_name:string; bytes:number };

// ---- Jobs panel (enqueue + poll + links) ----
function JobsPanel({ datasetId }: { datasetId?: string }) {
  const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
  const [y, setY] = useState("temperature");
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [polling, setPolling] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const enqueue = async () => {
    if (!datasetId) return;
    setErr(null);
    const url = `${API}/jobs?dataset_id=${datasetId}&y=${encodeURIComponent(y)}`;
    // Use authFetch for POST (protected)
    const r = await authFetch(url, { method: "POST" });
    const j = await r.json();
    if (!r.ok) { setErr(j?.detail || `Failed (${r.status})`); return; }
    setJobId(j.job_id); setStatus(j.status); setPolling(true);
  };

  // poll status
  useEffect(() => {
    if (!jobId || !polling) return;
    const t = setInterval(async () => {
      const r = await fetch(`${API}/jobs/${jobId}`);
      const j = await r.json();
      if (r.ok) {
        setStatus(j.status || j.db?.status || "unknown");
        if (j?.db?.result_summary) {
          try { setSummary(JSON.parse(j.db.result_summary)); } catch {}
        }
        if (["succeeded","failed","stopped"].includes(j.status)) setPolling(false);
      }
    }, 1500);
    return () => clearInterval(t);
  }, [jobId, polling]);

  const logsHref = jobId ? `${API}/jobs/${jobId}/logs` : undefined;
  const resultHref = jobId ? `${API}/jobs/${jobId}/result` : undefined;

  return (
    <div style={{border:"1px solid #eee", borderRadius:8, padding:12}}>
      <div style={{display:"flex", gap:8, alignItems:"center", marginBottom:8}}>
        <label>y:</label>
        <input value={y} onChange={e=>setY(e.target.value)} style={{border:"1px solid #ccc", padding:"4px 6px"}} />
        <button onClick={enqueue} style={{padding:"6px 10px", border:"1px solid #ccc", borderRadius:6}}>
          Enqueue job
        </button>
      </div>
      {err && <p style={{color:"#b00"}}>{err}</p>}
      {jobId && (
        <div>
          <p><b>job:</b> {jobId}</p>
          <p><b>status:</b> {status ?? "…"}</p>
          {summary && (
            <p><b>stats:</b> count={summary.count} min={summary.min} max={summary.max} mean={summary.mean}</p>
          )}
          <div style={{display:"flex", gap:12, marginTop:6}}>
            {logsHref && <a href={logsHref} target="_blank" rel="noreferrer">View logs</a>}
            {resultHref && <a href={resultHref}>Download result</a>}
          </div>
        </div>
      )}
    </div>
  );
}

export default function DatasetPage() {
  const router = useRouter();
  const id = router.query.id as string | undefined;

  const [preview, setPreview] = useState<PreviewResp | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);

  const [files, setFiles] = useState<FileRow[]>([]);
  const [filesError, setFilesError] = useState<string | null>(null);

  const [geo, setGeo] = useState<any>(null);
  const [geoError, setGeoError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    // preview
    fetch(`${API}/datasets/${id}/preview`)
      .then(async r => {
        const json = await r.json();
        if (!r.ok || json?.detail) {
          setPreviewError(json?.detail || `Preview failed (${r.status})`);
        } else {
          setPreview(json);
          setPreviewError(null);
        }
      })
      .catch(err => setPreviewError(String(err)));

    // files
    fetch(`${API}/datasets/${id}/files`)
      .then(async r => {
        const json = await r.json();
        if (!r.ok || json?.detail) setFilesError(json?.detail || `Files failed (${r.status})`);
        else { setFiles(json); setFilesError(null); }
      })
      .catch(err => setFilesError(String(err)));

    // geojson
    fetch(`${API}/datasets/${id}/geojson`)
      .then(async r => {
        const json = await r.json();
        if (!r.ok || json?.detail) setGeoError(json?.detail || `GeoJSON failed (${r.status})`);
        else { setGeo(json); setGeoError(null); }
      })
      .catch(err => setGeoError(String(err)));

  }, [id]);

  const imgSrc =
    id ? `${API}/datasets/${id}/timeseries?y=temperature&time_col=time&resample=D` : undefined;

  return (
    <main style={{padding:"16px", fontFamily:"Inter, system-ui, sans-serif"}}>
      <a href="/" style={{textDecoration:"underline"}}>← Back</a>
      <h1 style={{margin:"12px 0"}}>Dataset {id ?? ""}</h1>

      <section style={{marginBottom:24}}>
        <h3>Files</h3>
        {filesError && <p style={{color:"#b00"}}>{filesError}</p>}
        {!filesError && files.length === 0 && <p>No files found for this dataset.</p>}
        {files.length > 0 && (
          <ul>
            {files.map(f => <li key={f.file_id}>{f.original_name} <small>({f.bytes} bytes)</small></li>)}
          </ul>
        )}
      </section>

      {/* —— Revised preview section —— */}
      <section style={{marginBottom:24}}>
        <h3>Preview (first rows)</h3>
        {previewError && <p style={{color:"#b00"}}>{previewError}</p>}
        {!previewError && preview === null && <p>Loading…</p>}

        {/* guard & local alias */}
        {Array.isArray((preview as any)?.columns) && Array.isArray((preview as any)?.data) ? (() => {
          const p = preview as any; // has .columns and .data
          return (
            <div style={{overflowX:"auto", border:"1px solid #ddd", borderRadius:8}}>
              <table style={{borderCollapse:"collapse", width:"100%"}}>
                <thead>
                  <tr>
                    {(p.columns ?? []).map((c: any) => (
                      <th key={c.name} style={{textAlign:"left", padding:8, borderBottom:"1px solid #eee"}}>
                        {c.name} <small style={{color:"#666"}}>({c.dtype})</small>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(p.data ?? []).slice(0,20).map((row: any, i: number) => (
                    <tr key={i}>
                      {(p.columns ?? []).map((c: any) => (
                        <td key={c.name} style={{padding:8, borderBottom:"1px solid #f5f5f5"}}>
                          {String(row?.[c.name] ?? "")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        })() : (!previewError && preview !== null && (
          <p style={{color:"#b00"}}>Preview not available for this file.</p>
        ))}
      </section>

      <section style={{marginBottom:24}}>
        <h3>Time series (temperature vs time)</h3>
        {imgSrc ? (
          <img src={imgSrc} alt="timeseries" style={{maxWidth:"100%", border:"1px solid #eee", borderRadius:8}} />
        ) : <p>Loading chart…</p>}
      </section>

      {/* ---- Jobs panel added here ---- */}
      <section style={{marginBottom:24}}>
        <h3>Jobs</h3>
        <JobsPanel datasetId={id} />
      </section>

      <section style={{marginBottom:24}}>
        <h3>Map preview</h3>
        {geoError && <p style={{color:"#b00"}}>{geoError}</p>}
        {geo ? <MapClient data={geo} /> : (!geoError && <p>Loading map…</p>)}
      </section>
    </main>
  );
}

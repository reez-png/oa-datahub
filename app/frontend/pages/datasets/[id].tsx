import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";

const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
const MapClient = dynamic(() => import("../../components/MapClient"), { ssr: false });

type PreviewResp = {
  columns: { name: string; dtype: string; non_null: number }[];
  data: any[];
  stored_path: string;
};
type FileRow = { file_id:number; stored_path:string; original_name:string; bytes:number };

export default function DatasetPage() {
  const router = useRouter();
  const id = router.query.id as string;
  const [preview, setPreview] = useState<PreviewResp | null>(null);
  const [files, setFiles] = useState<FileRow[]>([]);
  const [geo, setGeo] = useState<any>(null);

  useEffect(() => {
    if (!id) return;
    fetch(`${API}/datasets/${id}/preview`).then(r => r.json()).then(setPreview).catch(console.error);
    fetch(`${API}/datasets/${id}/files`).then(r => r.json()).then(setFiles).catch(console.error);
    fetch(`${API}/datasets/${id}/geojson`).then(r => r.json()).then(setGeo).catch(console.error);
  }, [id]);

  const imgSrc = `${API}/datasets/${id}/timeseries?y=temperature&time_col=time&resample=D`;

  return (
    <main style={{padding:"16px", fontFamily:"Inter, system-ui, sans-serif"}}>
      <a href="/" style={{textDecoration:"underline"}}>← Back</a>
      <h1 style={{margin:"12px 0"}}>Dataset {id}</h1>

      <section style={{marginBottom:24}}>
        <h3>Files</h3>
        <ul>
          {files.map(f => <li key={f.file_id}>{f.original_name} <small>({f.bytes} bytes)</small></li>)}
        </ul>
      </section>

      <section style={{marginBottom:24}}>
        <h3>Preview (first rows)</h3>
        {!preview ? <p>Loading…</p> :
          <div style={{overflowX:"auto", border:"1px solid #ddd", borderRadius:8}}>
            <table style={{borderCollapse:"collapse", width:"100%"}}>
              <thead>
                <tr>
                  {preview.columns.map(c => (
                    <th key={c.name} style={{textAlign:"left", padding:8, borderBottom:"1px solid #eee"}}>
                      {c.name} <small style={{color:"#666"}}>({c.dtype})</small>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.data.slice(0,20).map((row, i) => (
                  <tr key={i}>
                    {preview.columns.map(c => (
                      <td key={c.name} style={{padding:8, borderBottom:"1px solid #f5f5f5"}}>
                        {String(row[c.name] ?? "")}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>}
      </section>

      <section style={{marginBottom:24}}>
        <h3>Time series (temperature vs time)</h3>
        <img src={imgSrc} alt="timeseries" style={{maxWidth:"100%", border:"1px solid #eee", borderRadius:8}} />
      </section>

      <section style={{marginBottom:24}}>
        <h3>Map preview</h3>
        {geo ? <MapClient data={geo} /> : <p>Loading map…</p>}
      </section>
    </main>
  );
}

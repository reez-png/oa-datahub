# app/api/src/app/main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os, io, csv
import chardet
import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.use("Agg")  # non-interactive backend for servers
import matplotlib.pyplot as plt

from sqlmodel import SQLModel, Field, select, Session
from typing import List, Optional
from datetime import date

# RQ + Redis
from redis import Redis
from rq import Queue

# Models & DB helpers
from app.models import Job
from app.db import create_db_and_tables, get_session

# ---- FastAPI app + CORS ----
app = FastAPI(title="OA DataHub API", version=os.getenv("APP_VERSION", "0.1.0"))

# allow your local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data/raw"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "oa-datahub", "version": os.getenv("APP_VERSION", "0.1.0")}

@app.get("/")
def root():
    return {"message": "Welcome to OA DataHub Lessons! Open /docs for the API UI."}

# ---------- Models ----------
class DatasetBase(SQLModel):
    name: str
    region: str
    start_date: date
    end_date: date
    source: str

class Dataset(DatasetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class DatasetRead(DatasetBase):
    id: int

class DatasetCreate(DatasetBase):
    pass

class FileRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    dataset_id: int = Field(index=True)
    original_name: str
    stored_path: str  # relative to /app (e.g., data/raw/1/file.csv)
    bytes: int

# ---------- Helpers ----------
def _get_queue() -> Queue:
    # Default to localhost unless REDIS_URL provided
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    conn = Redis.from_url(url)
    return Queue("default", connection=conn)

def _detect_encoding(sample: bytes) -> str:
    try:
        det = chardet.detect(sample)
        if det and det.get("encoding"):
            return det["encoding"]
    except Exception:
        pass
    return "utf-8"

def _detect_delimiter(text_sample: str) -> str:
    try:
        dialect = csv.Sniffer().sniff(text_sample, delimiters=";,|\t")
        return dialect.delimiter
    except Exception:
        return ","

def _read_csv_head(path: Path, nrows: int = 50) -> pd.DataFrame:
    raw = path.read_bytes()[:200_000]
    enc = _detect_encoding(raw)
    text = raw.decode(enc, errors="replace")
    delim = _detect_delimiter(text)
    return pd.read_csv(path, nrows=nrows, encoding=enc, sep=delim)

# --- alias mapper & sampled reader (used by geojson) ---
CANONICAL = {
    "time": ["time", "date", "datetime", "timestamp", "sample_time"],
    "latitude": ["latitude", "lat"],
    "longitude": ["longitude", "lon", "long", "lng"],
}

def _normalize_columns(df: pd.DataFrame) -> dict:
    """Map canonical names -> actual column names in df (best-effort)."""
    lower = {c.lower(): c for c in df.columns}
    mapping = {}
    for canon, alts in CANONICAL.items():
        for a in alts:
            if a.lower() in lower:
                mapping[canon] = lower[a.lower()]
                break
    return mapping

def _read_csv_sample(path: Path, max_rows: int = 5000) -> pd.DataFrame:
    """Read a moderate, bounded sample with sniffed encoding/delimiter."""
    raw = path.read_bytes()[:400_000]
    enc = _detect_encoding(raw)
    text = raw.decode(enc, errors="replace")
    delim = _detect_delimiter(text)
    return pd.read_csv(path, nrows=max_rows, encoding=enc, sep=delim)

# ---------- Dataset Endpoints ----------
@app.get("/datasets", response_model=List[DatasetRead])
def list_datasets(session: Session = Depends(get_session)):
    return session.exec(select(Dataset).order_by(Dataset.id)).all()

@app.post("/datasets", response_model=DatasetRead, status_code=201)
def create_dataset(d: DatasetCreate, session: Session = Depends(get_session)):
    item = Dataset(**d.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@app.get("/datasets/{dataset_id}", response_model=DatasetRead)
def get_dataset(dataset_id: int, session: Session = Depends(get_session)):
    item = session.get(Dataset, dataset_id)
    if not item:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return item

@app.delete("/datasets/{dataset_id}", status_code=204)
def delete_dataset(dataset_id: int, session: Session = Depends(get_session)):
    item = session.get(Dataset, dataset_id)
    if item:
        session.delete(item)
        session.commit()

# ---------- File Upload ----------
@app.post("/datasets/{dataset_id}/files", response_model=dict, status_code=201)
async def upload_file(dataset_id: int, f: UploadFile = File(...), session: Session = Depends(get_session)):
    ds = session.get(Dataset, dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    target_dir = DATA_DIR / str(dataset_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / f.filename
    content = await f.read()
    target_path.write_bytes(content)

    rel_path = target_path.relative_to(Path("/app"))
    rec = FileRecord(
        dataset_id=dataset_id,
        original_name=f.filename,
        stored_path=str(rel_path).replace("\\", "/"),
        bytes=len(content),
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)

    return {
        "file_id": rec.id,
        "dataset_id": dataset_id,
        "original_name": rec.original_name,
        "stored_path": rec.stored_path,
        "bytes": rec.bytes,
        "tip": "Saved under data/raw/<dataset_id>/ on your host.",
    }

# ---------- Jobs (enqueue + status) ----------
@app.post("/jobs", response_model=dict, status_code=202)
def create_job(
    dataset_id: int,
    file_id: int | None = None,
    y: str = "temperature",
    session: Session = Depends(get_session),
):
    q = select(FileRecord).where(FileRecord.dataset_id == dataset_id)
    q = q.where(FileRecord.id == file_id) if file_id else q.order_by(FileRecord.id.desc())
    rec = session.exec(q).first()
    if not rec:
        raise HTTPException(status_code=404, detail="No files found for this dataset")

    q_ = _get_queue()
    # enqueue by string path to avoid importing tasks here
    job = q_.enqueue("app.tasks.process_csv", dataset_id, rec.stored_path, y, job_timeout=600)

    item = Job(id=job.id, dataset_id=dataset_id, file_path=rec.stored_path, type="process_csv", status="queued")
    session.add(item)
    session.commit()

    return {"job_id": job.id, "status": "queued", "dataset_id": dataset_id, "file_id": rec.id, "y": y}

@app.get("/jobs/{job_id}", response_model=dict)
def get_job(job_id: str, session: Session = Depends(get_session)):
    q_ = _get_queue()
    rq_job = q_.fetch_job(job_id)
    db_job = session.get(Job, job_id)

    if not rq_job and not db_job:
        raise HTTPException(status_code=404, detail="Job not found")

    status = rq_job.get_status() if rq_job else (db_job.status if db_job else "unknown")
    return {
        "job_id": job_id,
        "status": status,
        "db": {
            "dataset_id": db_job.dataset_id if db_job else None,
            "file_path": db_job.file_path if db_job else None,
            "result_path": getattr(db_job, "result_path", None) if db_job else None,
            "result_summary": getattr(db_job, "result_summary", None) if db_job else None,
            "type": getattr(db_job, "type", None) if db_job else None,
        },
    }

# ---------- Geo preview (GeoJSON) ----------
def _pick_col(mapping: dict, explicit: Optional[str], key: str) -> str:
    if explicit:
        return explicit
    if key not in mapping:
        raise HTTPException(status_code=400, detail=f"Column for '{key}' not found and no alias provided.")
    return mapping[key]

@app.get("/datasets/{dataset_id}/geojson", response_model=dict)
def dataset_geojson(
    dataset_id: int,
    file_id: Optional[int] = None,
    lat_col: Optional[str] = None,
    lon_col: Optional[str] = None,
    time_col: Optional[str] = None,
    value_cols: Optional[str] = None,   # comma-separated list to include as properties
    limit: int = 5000,
    bbox: Optional[str] = None,         # "minLon,minLat,maxLon,maxLat"
    session: Session = Depends(get_session),
):
    # choose file (latest if not specified)
    q = select(FileRecord).where(FileRecord.dataset_id == dataset_id)
    q = q.where(FileRecord.id == file_id) if file_id is not None else q.order_by(FileRecord.id.desc())
    rec = session.exec(q).first()
    if not rec:
        raise HTTPException(status_code=404, detail="No files found for this dataset")

    path = Path("/app") / rec.stored_path
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found on disk: {rec.stored_path}")

    try:
        df = _read_csv_sample(path, max_rows=max(1000, min(limit * 5, 50000)))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {e}")

    # map canonical aliases (from earlier helpers)
    mapping = _normalize_columns(df)

    # decide columns to use
    lat_name = lat_col or mapping.get("latitude")
    lon_name = lon_col or mapping.get("longitude")
    if not lat_name or not lon_name:
        raise HTTPException(status_code=400, detail="Latitude/Longitude columns not found. Provide lat_col/lon_col or rename columns.")

    t_name = time_col or mapping.get("time")

    # numeric conversions + validity mask
    lat = pd.to_numeric(df[lat_name], errors="coerce")
    lon = pd.to_numeric(df[lon_name], errors="coerce")
    mask = ~(lat.isna() | lon.isna() | (lat < -90) | (lat > 90) | (lon < -180) | (lon > 180))

    # optional bbox filter
    if bbox:
        try:
            mnL, mnA, mxL, mxA = [float(x) for x in bbox.split(",")]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid bbox. Use 'minLon,minLat,maxLon,maxLat'.")
        mask &= (lon >= mnL) & (lon <= mxL) & (lat >= mnA) & (lat <= mxA)

    d = df.loc[mask].copy()
    if d.empty:
        return {"type": "FeatureCollection", "features": []}

    # choose value columns to include in properties
    props_cols: List[str] = []
    if value_cols:
        for c in [c.strip() for c in value_cols.split(",") if c.strip()]:
            if c in d.columns:
                props_cols.append(c)

    # time column (optional)
    if t_name and t_name in d.columns:
        t_ser = pd.to_datetime(d[t_name], errors="coerce", utc=True)
    else:
        t_ser = None

    # build features (cap by limit for responsiveness)
    feats = []
    for i, row in d.head(limit).iterrows():
        props: dict = {}
        if t_ser is not None:
            ts = t_ser.loc[i]
            if pd.notna(ts):
                props["time"] = ts.isoformat()
        for c in props_cols:
            val = row[c]
            if pd.isna(val):
                continue
            props[c] = float(val) if isinstance(val, (int, float, np.number)) else str(val)

        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(row[lon_name]), float(row[lat_name])]},
            "properties": props
        })

    return {"type": "FeatureCollection", "features": feats}

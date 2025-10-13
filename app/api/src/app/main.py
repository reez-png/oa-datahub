# app/api/src/app/main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, Response
from pathlib import Path
import os
from typing import List, Optional
from datetime import date
from sqlmodel import SQLModel, Field, select, Session

# --- CSV/preview/validation/plotting imports ---
import io
import csv
import chardet
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")  # non-interactive backend for servers
import matplotlib.pyplot as plt

from app.db import create_db_and_tables, get_session

# ---- App + config ----
app = FastAPI(title="OMI-OA DataHub API", version=os.getenv("APP_VERSION", "0.1.0"))

# Where raw files are stored (mapped to ./data/raw on your host via docker-compose)
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

# ---------- Datasets (DB-backed) ----------

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

@app.get("/datasets", response_model=List[DatasetRead])
def list_datasets(session: Session = Depends(get_session)):
    results = session.exec(select(Dataset).order_by(Dataset.id))
    return results.all()

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
    if not item:
        return
    session.delete(item)
    session.commit()

# ---------- Files (DB-backed) ----------

class FileRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    dataset_id: int = Field(index=True)
    original_name: str
    stored_path: str  # path relative to project root (e.g., data/raw/123/file.csv)
    bytes: int

# Upload a file for a dataset
@app.post("/datasets/{dataset_id}/files", response_model=dict, status_code=201)
async def upload_file(
    dataset_id: int,
    f: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    ds = session.get(Dataset, dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Ensure subfolder exists: data/raw/<dataset_id>/
    target_dir = DATA_DIR / str(dataset_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    # Save file (stream -> disk)
    target_path = target_dir / f.filename
    content = await f.read()
    target_path.write_bytes(content)

    # Record in DB; store path relative to container workdir (/app)
    project_root = Path("/app")
    rel_path = target_path.relative_to(project_root)

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
        "tip": "Saved under data/raw/<dataset_id>/ on your host (via bind mount).",
    }

# List files for a dataset
@app.get("/datasets/{dataset_id}/files", response_model=list[dict])
def list_dataset_files(dataset_id: int, session: Session = Depends(get_session)):
    ds = session.get(Dataset, dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    rows = session.exec(
        select(FileRecord).where(FileRecord.dataset_id == dataset_id).order_by(FileRecord.id)
    ).all()
    return [
        {
            "file_id": r.id,
            "dataset_id": r.dataset_id,
            "original_name": r.original_name,
            "stored_path": r.stored_path,
            "bytes": r.bytes,
        }
        for r in rows
    ]

# ---------- CSV preview helpers ----------

def _detect_encoding(sample: bytes) -> str:
    try:
        det = chardet.detect(sample)
        if det and det.get("encoding"):
            return det["encoding"]
    except Exception:
        pass
    return "utf-8"  # safe default

def _detect_delimiter(text_sample: str) -> str:
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(text_sample, delimiters=";,|\t")
        return dialect.delimiter
    except Exception:
        return ","  # default to comma

def _read_csv_head(path: Path, nrows: int = 50) -> pd.DataFrame:
    raw = path.read_bytes()[:200_000]  # sample up to 200 KB for sniffing
    enc = _detect_encoding(raw)
    text = raw.decode(enc, errors="replace")
    delim = _detect_delimiter(text)
    return pd.read_csv(path, nrows=nrows, encoding=enc, sep=delim)

def _df_schema(df: pd.DataFrame) -> list[dict]:
    out = []
    nn = df.notna().sum()
    for col in df.columns:
        out.append({
            "name": col,
            "dtype": str(df[col].dtype),
            "non_null": int(nn[col]),
        })
    return out

@app.get("/datasets/{dataset_id}/preview", response_model=dict)
def preview_dataset(
    dataset_id: int,
    file_id: Optional[int] = None,
    nrows: int = 50,
    session: Session = Depends(get_session),
):
    # Choose which file to preview
    q = select(FileRecord).where(FileRecord.dataset_id == dataset_id)
    if file_id is not None:
        q = q.where(FileRecord.id == file_id)
    else:
        q = q.order_by(FileRecord.id.desc())  # latest by default
    rec = session.exec(q).first()
    if not rec:
        raise HTTPException(status_code=404, detail="No files found for this dataset")

    # Resolve to the mounted path
    path = Path("/app") / rec.stored_path  # e.g., /app/data/raw/<id>/file.csv
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found on disk: {rec.stored_path}")

    try:
        df = _read_csv_head(path, nrows=max(1, min(nrows, 200)))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {e}")

    # Build a small, JSON-safe payload
    sample = df.head(min(len(df), nrows)).fillna("").astype(str).to_dict(orient="records")
    return {
        "file_id": rec.id,
        "stored_path": rec.stored_path,
        "rows_previewed": len(sample),
        "columns": _df_schema(df),
        "data": sample,
        "note": "This is a preview; we only read the first chunk.",
    }

# ---------- Validation helpers (Temperature) ----------

CANONICAL = {
    "time": ["time", "date", "datetime", "timestamp", "sample_time"],
    "latitude": ["latitude", "lat"],
    "longitude": ["longitude", "lon", "long", "lng"],
    # temperature in °C — include common aliases
    "temperature": ["temperature", "temp", "temp_wat", "temp_water", "t", "sst", "watertemp", "temp_c", "temperature_c"],
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
    """Read a larger sample than preview for better validation, still bounded."""
    raw = path.read_bytes()[:400_000]  # bigger sniff window than preview
    enc = _detect_encoding(raw)
    text = raw.decode(enc, errors="replace")
    delim = _detect_delimiter(text)
    return pd.read_csv(path, nrows=max_rows, encoding=enc, sep=delim)

@app.get("/datasets/{dataset_id}/validate", response_model=dict)
def validate_dataset(
    dataset_id: int,
    file_id: Optional[int] = None,
    nrows: int = 5000,
    session: Session = Depends(get_session),
):
    # Pick file (latest if file_id not provided)
    q = select(FileRecord).where(FileRecord.dataset_id == dataset_id)
    q = q.where(FileRecord.id == file_id) if file_id is not None else q.order_by(FileRecord.id.desc())
    rec = session.exec(q).first()
    if not rec:
        raise HTTPException(status_code=404, detail="No files found for this dataset")

    path = Path("/app") / rec.stored_path
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found on disk: {rec.stored_path}")

    # Read bounded sample
    try:
        df = _read_csv_sample(path, max_rows=max(100, min(nrows, 20000)))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {e}")

    mapping = _normalize_columns(df)
    required = ["time", "latitude", "longitude", "temperature"]
    missing = [k for k in required if k not in mapping]

    issues = []
    if missing:
        issues.append({
            "type": "missing_columns",
            "detail": f"Missing required columns (or aliases): {missing}",
            "hint": "Rename or supply column aliases (e.g., lat/latitude, lon/longitude, time/date, temp/temp_wat)."
        })
        return {
            "file_id": rec.id,
            "stored_path": rec.stored_path,
            "rows_checked": int(len(df)),
            "column_mapping": mapping,
            "issues": issues,
        }

    # Parse/validate fields
    # time
    tcol = mapping["time"]
    t = pd.to_datetime(df[tcol], errors="coerce", utc=True)
    bad_time = int(t.isna().sum())

    # latitude / longitude
    lat = pd.to_numeric(df[mapping["latitude"]], errors="coerce")
    lon = pd.to_numeric(df[mapping["longitude"]], errors="coerce")
    bad_lat = int(((lat < -90) | (lat > 90) | lat.isna()).sum())
    bad_lon = int(((lon < -180) | (lon > 180) | lon.isna()).sum())

    # Temperature (°C), basic physical range
    tcol_temp = mapping["temperature"]
    temperature = pd.to_numeric(df[tcol_temp], errors="coerce")
    bad_temperature = int(((temperature < -2) | (temperature > 45) | temperature.isna()).sum())

    # Collect a few problematic rows
    sample_bad = []
    for idx in df.index[:2000]:  # bounded scan for speed
        flags = []
        if pd.isna(t.iloc[idx]): flags.append("time")
        if pd.isna(lat.iloc[idx]) or (lat.iloc[idx] < -90) or (lat.iloc[idx] > 90): flags.append("latitude")
        if pd.isna(lon.iloc[idx]) or (lon.iloc[idx] < -180) or (lon.iloc[idx] > 180): flags.append("longitude")
        if pd.isna(temperature.iloc[idx]) or (temperature.iloc[idx] < -2) or (temperature.iloc[idx] > 45): flags.append("temperature")
        if flags:
            sample_bad.append({"row": int(idx), "columns": flags})
        if len(sample_bad) >= 10:
            break

    # Summarize issues
    if bad_time:
        issues.append({"type": "invalid_time", "count": bad_time, "hint": "Ensure ISO timestamps or recognizable date formats."})
    if bad_lat:
        issues.append({"type": "invalid_latitude", "count": bad_lat, "hint": "Latitude must be in [-90, 90]."})
    if bad_lon:
        issues.append({"type": "invalid_longitude", "count": bad_lon, "hint": "Longitude must be in [-180, 180]."})
    if bad_temperature:
        issues.append({"type": "invalid_temperature", "count": bad_temperature, "hint": "Temperature (°C) should be roughly −2 to 45. Check units/format."})

    return {
        "file_id": rec.id,
        "stored_path": rec.stored_path,
        "rows_checked": int(len(df)),
        "column_mapping": mapping,
        "issues": issues,
        "bad_rows_sample": sample_bad,
        "note": "Validation uses a sampled read; fix columns/units then re-upload for best results."
    }

# ---------- Full-read helper (used by /timeseries and /export) ----------

def _read_csv_full(path: Path) -> pd.DataFrame:
    raw = path.read_bytes()[:400_000]
    enc = _detect_encoding(raw)
    text = raw.decode(enc, errors="replace")
    delim = _detect_delimiter(text)
    return pd.read_csv(path, encoding=enc, sep=delim)

# ---------- Time-series plot (PNG) ----------

@app.get("/datasets/{dataset_id}/timeseries")
def plot_timeseries(
    dataset_id: int,
    y: str,                     # e.g., "temperature"
    time_col: str = "time",
    file_id: Optional[int] = None,
    resample: Optional[str] = None,  # e.g., "D" (daily), "M" (monthly)
    session: Session = Depends(get_session),
):
    # pick a file (latest if not specified)
    q = select(FileRecord).where(FileRecord.dataset_id == dataset_id)
    q = q.where(FileRecord.id == file_id) if file_id is not None else q.order_by(FileRecord.id.desc())
    rec = session.exec(q).first()
    if not rec:
        raise HTTPException(status_code=404, detail="No files found for this dataset")

    path = Path("/app") / rec.stored_path
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found on disk: {rec.stored_path}")

    try:
        df = _read_csv_full(path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {e}")

    # basic guards
    if time_col not in df.columns:
        raise HTTPException(status_code=400, detail=f"Time column '{time_col}' not found.")
    if y not in df.columns:
        raise HTTPException(status_code=400, detail=f"Y column '{y}' not found.")

    # parse + clean
    t = pd.to_datetime(df[time_col], errors="coerce", utc=True)
    s = pd.to_numeric(df[y], errors="coerce")
    sel = ~(t.isna() | s.isna())
    ts = pd.DataFrame({"t": t[sel], "y": s[sel]}).sort_values("t").set_index("t")

    if ts.empty:
        raise HTTPException(status_code=400, detail="No valid (time, value) rows to plot.")

    if resample:
        try:
            ts = ts.resample(resample).mean()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid resample rule (try 'D' or 'M').")

    # plot
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(ts.index, ts["y"])
    ax.set_xlabel(time_col)
    ax.set_ylabel(y)
    ax.set_title(f"{y} vs {time_col}")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

# ---------- CSV export (select columns; optional row limit) ----------

@app.get("/datasets/{dataset_id}/export")
def export_dataset_csv(
    dataset_id: int,
    file_id: Optional[int] = None,
    columns: Optional[str] = None,   # comma-separated list
    limit: Optional[int] = None,
    session: Session = Depends(get_session),
):
    q = select(FileRecord).where(FileRecord.dataset_id == dataset_id)
    q = q.where(FileRecord.id == file_id) if file_id is not None else q.order_by(FileRecord.id.desc())
    rec = session.exec(q).first()
    if not rec:
        raise HTTPException(status_code=404, detail="No files found for this dataset")

    path = Path("/app") / rec.stored_path
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found on disk: {rec.stored_path}")

    try:
        df = _read_csv_full(path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {e}")

    if columns:
        keep = [c.strip() for c in columns.split(",") if c.strip()]
        missing = [c for c in keep if c not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Columns not found: {missing}")
        df = df[keep]

    if limit is not None:
        try:
            n = max(1, int(limit))
        except ValueError:
            raise HTTPException(status_code=400, detail="limit must be an integer")
        df = df.head(n)

    # stream CSV
    def _iter():
        yield df.to_csv(index=False)

    filename = Path(rec.original_name).with_suffix(".filtered.csv").name
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(_iter(), media_type="text/csv", headers=headers)

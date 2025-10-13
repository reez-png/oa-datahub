# app/api/src/app/main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pathlib import Path
import os, io, csv
import chardet
import pandas as pd
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

app = FastAPI(title="OMI-OA DataHub API", version=os.getenv("APP_VERSION", "0.1.0"))

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
    # per your note: default to localhost unless REDIS_URL provided
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

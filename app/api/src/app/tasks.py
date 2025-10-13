from __future__ import annotations
import os, json
from pathlib import Path
from datetime import datetime

import pandas as pd
from sqlmodel import Session
from rq import get_current_job

from app.db import engine
from app.models import Job  # Job model is defined in app/models.py

RAW_DIR = Path(os.getenv("DATA_DIR", "/app/data/raw"))
PROC_DIR = Path(os.getenv("DATA_PROCESSED", "/app/data/processed"))
PROC_DIR.mkdir(parents=True, exist_ok=True)

# --- simple per-job logfile ---
LOG_DIR = PROC_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def _log(job_id: str, msg: str):
    p = LOG_DIR / f"{job_id}.log"
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def process_csv(dataset_id: int, file_rel_path: str, y: str = "temperature") -> dict:
    """Demo job: read CSV, compute quick stats, write a processed file, and log steps."""
    job = get_current_job()
    job_id = job.id if job else "nojob"

    _log(job_id, f"Start process_csv dataset={dataset_id} file={file_rel_path} y={y}")

    # paths
    src = Path("/app") / file_rel_path            # e.g., data/raw/1/water.csv
    out_dir = PROC_DIR / str(dataset_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / f"processed_{Path(file_rel_path).name}"

    # read & compute
    df = pd.read_csv(src)
    if y not in df.columns:
        _log(job_id, f"ERROR: column '{y}' not found. Available: {list(df.columns)[:10]}...")
        raise ValueError(f"Column '{y}' not in file")

    s = pd.to_numeric(df[y], errors="coerce")
    stats = {
        "count": int(s.notna().sum()),
        "min": float(s.min()) if s.notna().any() else None,
        "max": float(s.max()) if s.notna().any() else None,
        "mean": float(s.mean()) if s.notna().any() else None,
    }
    _log(job_id, f"Stats {stats}")

    # write a trivial "processed" file (copy with one extra column)
    df_out = df.copy()
    df_out[f"{y}_centered"] = s - s.mean()
    df_out.to_csv(out_csv, index=False)
    _log(job_id, f"Wrote {out_csv}")

    # record back to DB
    with Session(engine) as session:
        db_job = session.get(Job, job_id)
        if db_job:
            db_job.status = "succeeded"
            db_job.result_path = str(out_csv.relative_to(Path("/app")))
            db_job.result_summary = json.dumps(stats)
            session.add(db_job)
            session.commit()
    _log(job_id, "Done")

    return {"job_id": job_id, "output": str(out_csv), "stats": stats}

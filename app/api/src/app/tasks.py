from __future__ import annotations
import os, json
from pathlib import Path
import pandas as pd
from sqlmodel import Session
from rq import get_current_job

from app.db import get_session, engine
from app.models import Job  # we'll add Job model below

RAW_DIR = Path(os.getenv("DATA_DIR", "/app/data/raw"))
PROC_DIR = Path(os.getenv("DATA_PROCESSED", "/app/data/processed"))
PROC_DIR.mkdir(parents=True, exist_ok=True)

def process_csv(dataset_id: int, file_rel_path: str, y: str = "temperature") -> dict:
    """Demo job: read CSV, compute quick stats, write a processed file."""
    job = get_current_job()
    job_id = job.id if job else "nojob"

    # paths
    src = Path("/app") / file_rel_path            # e.g., data/raw/1/water_co2.csv
    out_dir = PROC_DIR / str(dataset_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / f"processed_{Path(file_rel_path).name}"

    # read & compute
    df = pd.read_csv(src)
    if y not in df.columns:
        raise ValueError(f"Column '{y}' not in file. Available: {list(df.columns)[:10]}...")

    # basic numeric cleaning
    s = pd.to_numeric(df[y], errors="coerce")
    stats = {
        "count": int(s.notna().sum()),
        "min": float(s.min()) if s.notna().any() else None,
        "max": float(s.max()) if s.notna().any() else None,
        "mean": float(s.mean()) if s.notna().any() else None,
    }

    # write a trivial "processed" file (copy with one extra column)
    df_out = df.copy()
    df_out[f"{y}_centered"] = s - s.mean()
    df_out.to_csv(out_csv, index=False)

    # record back to DB
    with Session(engine) as session:
        db_job = session.get(Job, job_id)
        if db_job:
            db_job.status = "succeeded"
            db_job.result_path = str(out_csv.relative_to(Path("/app")))
            db_job.result_summary = json.dumps(stats)
            session.add(db_job)
            session.commit()

    return {"job_id": job_id, "output": str(out_csv), "stats": stats}

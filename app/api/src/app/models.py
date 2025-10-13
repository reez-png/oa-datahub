# app/api/src/app/models.py
from typing import Optional
from sqlmodel import SQLModel, Field

class Job(SQLModel, table=True):
    id: str = Field(primary_key=True)        # rq job id
    dataset_id: int
    file_path: str                           # e.g., data/raw/1/water.csv
    type: str                                # e.g., "process_csv"
    status: str = "queued"                   # queued|started|succeeded|failed
    result_path: Optional[str] = None        # relative path to output in container, e.g., data/processed/1/...
    result_summary: Optional[str] = None     # JSON with quick stats

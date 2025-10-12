# app/api/src/app/main.py
from fastapi import FastAPI, Depends, HTTPException
import os
from typing import List
from datetime import date
from sqlmodel import SQLModel, Field, select, Session

from app.db import create_db_and_tables, get_session

app = FastAPI(title="OA DataHub (Lesson 2C)", version=os.getenv("APP_VERSION", "0.1.0"))

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

# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import date

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# ----- Lesson 2A: in-memory datasets -----

class DatasetIn(BaseModel):
    name: str
    region: str
    start_date: date
    end_date: date
    source: str

class Dataset(DatasetIn):
    id: int

DATASETS: List[Dataset] = []
_next_id = 1

@app.get("/datasets", response_model=List[Dataset])
def list_datasets():
    return DATASETS

@app.post("/datasets", response_model=Dataset, status_code=201)
def create_dataset(d: DatasetIn):
    global _next_id
    # Pydantic v2: use model_dump() (v1 would be dict())
    item = Dataset(id=_next_id, **d.model_dump())
    _next_id += 1
    DATASETS.append(item)
    return item

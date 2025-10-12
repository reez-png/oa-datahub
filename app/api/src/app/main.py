from fastapi import FastAPI
import os

app = FastAPI(title="OA DataHub (Lesson 1)", version=os.getenv("APP_VERSION", "0.1.0"))

@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "service": "oa-datahub",
        "version": os.getenv("APP_VERSION", "0.1.0"),
    }

@app.get("/")
def root():
    return {"message": "Welcome to OA DataHub Lesson 1! Open /docs for the API UI."}

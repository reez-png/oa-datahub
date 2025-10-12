# OA DataHub — Lesson 1 Starter

Welcome! This is a minimal, **beginner-friendly** starting point for your web app journey.
In Lesson 1 you'll:
- Install the basics (Git, Python, Docker) and sign into GitHub
- Run a tiny API using **FastAPI**
- Make your first commit and push to GitHub
- Call a `/healthz` endpoint and see JSON come back

## 0) Install prerequisites

- **Git**: https://git-scm.com/downloads
- **Python 3.11+**:
  - Windows: https://www.python.org/downloads/windows/ (check “Add Python to PATH”)
  - Linux/macOS: use your package manager or official installer
- **Docker Desktop** (optional in Lesson 1, required later): https://www.docker.com/products/docker-desktop/

Create a **GitHub** account if you don't have one: https://github.com/join

---

## 1) Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
cd app\api
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**macOS/Linux (bash/zsh):**
```bash
cd app/api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2) Run the API locally

```bash
uvicorn app.main:app --reload --port 8000
```

Now open your browser at:
- http://localhost:8000/healthz  → should return `{"status":"ok","service":"oa-datahub","version":"0.1.0"}`
- http://localhost:8000/docs     → interactive API docs (Swagger UI)

---

## 3) Initialize a Git repo and make your first commit

From the **project root** (the folder containing this README):

```bash
git init
git add .
git commit -m "Lesson 1: initialize OA DataHub starter (FastAPI hello)"
```

Create a **new empty repo on GitHub** (web UI) called, for example, `oa-datahub`.

Then connect and push:

```bash
git branch -M main
git remote add origin https://github.com/<YOUR-USER>/oa-datahub.git
git push -u origin main
```

---

## 4) (Optional) Run with Docker

Make sure Docker Desktop is running.

From the project root:

```bash
docker compose up --build
```

Test it:
- http://localhost:8000/healthz
- http://localhost:8000/docs

Stop it with `Ctrl+C`, then `docker compose down` to remove containers.

---

## 5) Next steps (sneak peek for Lesson 2)
- Add a simple `/datasets` endpoint
- Persist to a real database (Postgres)
- Add a tiny frontend page

---

## Troubleshooting

- If `uvicorn` not found, ensure the venv is **activated** and `pip install -r requirements.txt` succeeded.
- If port 8000 is busy, change `--port 8001` (and open that URL).
- On Windows PowerShell, if scripts are blocked, run as Admin:
  `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

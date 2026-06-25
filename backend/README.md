# Backend

FastAPI backend for the AI Marketing Partner.

## Run Locally

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check:

```text
GET http://localhost:8000/health
```

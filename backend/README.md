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

Swagger UI:

```text
http://localhost:8000/docs
```

Protected routes use Firebase bearer auth. In Swagger, click **Authorize** and paste a Firebase ID token without the `Bearer` prefix.

Protected routes require Firebase Admin credentials.

Recommended local setup:

```text
FIREBASE_SERVICE_ACCOUNT_FILE=C:\absolute\path\to\service-account.json
FIREBASE_STORAGE_BUCKET=ai-agent-dhaanyashree.firebasestorage.app
```

Alternative inline setup:

```text
FIREBASE_PROJECT_ID=
FIREBASE_CLIENT_EMAIL=
FIREBASE_PRIVATE_KEY=
FIREBASE_STORAGE_BUCKET=
```

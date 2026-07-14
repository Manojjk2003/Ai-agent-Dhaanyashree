# AI Marketing Partner

AI Marketing Partner is planned as a dashboard and agent system for small business marketing. The first foundation includes:

- React + Vite frontend in `frontend/`
- FastAPI backend in `backend/`
- LangGraph workflow location in `backend/app/graphs/`
- Manual content review and calendar scheduling
- Project memory and architecture docs at the root

## Project Layout

```text
.
|-- frontend/
|-- backend/
|-- memory.md
|-- architecture.md
|-- routes.md
|-- api-map.md
|-- database-map.md
|-- dependency-graph.md
|-- plan.md
|-- .env.example
`-- .gitignore
```

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend health check:

```text
http://localhost:8000/health
```

Swagger UI:

```text
http://localhost:8000/docs
```

For protected routes, log in from the frontend, copy the Firebase ID token from the dashboard, click **Authorize** in Swagger, and paste the token without the `Bearer` prefix.

Protected backend routes need Firebase Admin credentials in `backend/.env` or the shell environment.

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

Gemini-backed daily content generation can be enabled with:

```text
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-3.5-flash
GEMINI_API_KEY=<your-google-ai-studio-key>
```

Create or view Gemini API keys from:

```text
https://aistudio.google.com/api-keys
```

The backend keeps this key server-side and falls back to rule-based generation if Gemini is unavailable.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend dev server:

```text
http://localhost:5173
```

The frontend reads Firebase Web SDK settings from `frontend/.env.local`.

Enable the Email/Password provider in Firebase Authentication before using the login screen:

1. Open Firebase Console.
2. Select the `ai-agent-dhaanyashree` project.
3. Go to Authentication.
4. Click Get started if Authentication has not been initialized.
5. Open Sign-in method.
6. Enable Email/Password.

## Documentation Rule

When implementation changes, update the matching documentation in the same work session:

- Architecture: `architecture.md` and `memory.md`
- Routes: `routes.md`
- APIs: `api-map.md`
- Database/storage: `database-map.md`
- Dependencies/modules: `dependency-graph.md`

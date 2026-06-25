# AI Marketing Partner

AI Marketing Partner is planned as a dashboard and agent system for small business marketing. The first foundation includes:

- React + Vite frontend in `frontend/`
- FastAPI backend in `backend/`
- LangGraph workflow location in `backend/app/graphs/`
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

## Documentation Rule

When implementation changes, update the matching documentation in the same work session:

- Architecture: `architecture.md` and `memory.md`
- Routes: `routes.md`
- APIs: `api-map.md`
- Database/storage: `database-map.md`
- Dependencies/modules: `dependency-graph.md`

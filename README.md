# AI Marketing Partner

AI Marketing Partner is planned as a dashboard and agent system for small business marketing. The first foundation includes:

- React + Vite frontend in `frontend/`
- FastAPI backend in `backend/`
- LangGraph workflow location in `backend/app/graphs/`
- Manual content review and calendar scheduling
- Firebase Storage uploads for brand, reference, product, and generated poster images
- Project memory and architecture docs at the root

The official phase map and remaining roadmap live in `plan.md`. Current completed scope is Phases 1-15; pending roadmap includes analytics, recommendations, SEO, blogs, campaign planning, video/reels, trend intelligence, agent logs, real reference-image generation, and sales intelligence.

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
FIREBASE_TOKEN_CLOCK_SKEW_SECONDS=10
```

Alternative inline setup:

```text
FIREBASE_PROJECT_ID=
FIREBASE_CLIENT_EMAIL=
FIREBASE_PRIVATE_KEY=
FIREBASE_STORAGE_BUCKET=
FIREBASE_TOKEN_CLOCK_SKEW_SECONDS=10
```

`FIREBASE_TOKEN_CLOCK_SKEW_SECONDS` allows a small clock tolerance for Firebase ID tokens. Keep it small; `10` seconds handles local machine drift like `Token used too early` errors.

Gemini-backed daily content generation can be enabled with:

```text
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-3.5-flash
GEMINI_IMAGE_MODEL=gemini-3.1-flash-image
GEMINI_API_KEY=<your-google-ai-studio-key>
BACKEND_PUBLIC_URL=http://localhost:8000
```

Create or view Gemini API keys from:

```text
https://aistudio.google.com/api-keys
```

The backend keeps this key server-side and falls back to rule-based text generation when Gemini is unavailable, returns invalid JSON, or hits quota/rate limits such as HTTP 429. Daily content and schedule recommendations request low thinking to reduce latency and token usage.

Poster image generation can use Hugging Face FLUX with:

```text
IMAGE_PROVIDER=huggingface
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell
HF_TOKEN=<your-hugging-face-token>
```

Create a Hugging Face token from:

```text
https://huggingface.co/settings/tokens
```

The token needs permission to make Inference Providers calls. If the image provider is unavailable, the backend saves a fallback SVG poster and stores the fallback reason in Firestore.

Image uploads and generated posters use Firebase Storage when `FIREBASE_STORAGE_BUCKET` is configured. Brand logo/avatar uploads, reference images, product image galleries, and generated poster files are routed through the backend so secrets stay server-side. Brand kit, uploaded product images, and labelled reference images are used as active generation context. When a brand logo is uploaded and saved in the business profile, generated raster posters are stamped with that logo at the top before being stored. When product images exist, the first uploaded product image is composited into the final raster poster.

Social publishing defaults to a safe mock workflow. The Calendar **Publish Now** button marks the scheduled/generated post as published and records a platform post id. When Meta credentials are configured, the same button publishes through Meta Graph API.

Meta publishing can be enabled server-side with:

```text
SOCIAL_PROVIDER=meta
META_GRAPH_API_VERSION=v23.0
META_PAGE_ID=<facebook-page-id>
META_PAGE_ACCESS_TOKEN=<page-access-token>
META_INSTAGRAM_BUSINESS_ACCOUNT_ID=<instagram-business-account-id>
```

When configured, **Publish Now** uses the latest generated poster for the scheduled post and publishes through Meta Graph API. Without these values, the app keeps using the mock publisher.

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

# AI Marketing Partner - Project Memory

## Documentation Maintenance Rule

Whenever code, configuration, routes, APIs, database schema, agent behavior, deployment, or integrations change, update the matching project document in the same work session.

- Architecture changes: update `architecture.md` and this file.
- Route changes: update `routes.md`.
- API changes: update `api-map.md`.
- Database or storage changes: update `database-map.md`.
- Dependency or module ownership changes: update `dependency-graph.md`.
- Feature behavior changes: update this file under Feature Inventory and Data Flows.

## Project Overview

The project is intended to become an AI Marketing Partner for small business owners. The system should understand the business, products, audience, brand tone, trends, content performance, and sales signals, then generate marketing actions such as captions, posters, reels, SEO ideas, calendar plans, and recommendations.

Current repository state: Phase 13 foundation scaffold exists. The workspace now contains a React/Vite frontend with Firebase Auth initialization, email/password auth UI, protected app shell, one business profile form with brand kit uploads, product management with multiple uploaded image URLs, reference image memory with uploads, daily marketing plan generation, generated content review, manual content calendar scheduling, AI schedule time recommendation, poster image generation/preview, mock publish controls, a FastAPI backend with Firebase token verification plus asset-upload/business/product/reference-image/content/schedule/poster/social/agent routes, Gemini-backed daily generation, Hugging Face FLUX/Gemini poster image generation paths with fallback SVG output, Firebase Storage upload support, brand-grounded prompt generation, final logo/product-image poster composition, root environment/ignore/readme files, and project memory documents.

Verified from repository: `git status` reports this is not a valid Git repository, even though a `.git` entry is present in the workspace.

## Business Purpose

The business problem is that small business owners need consistent marketing but often lack time, strategy, design capability, SEO knowledge, trend awareness, and analytics discipline.

The app model is one signed-in user with one business profile and many products:

```text
User account
  -> One business profile
      -> Many products
```

Firestore uses one `businesses/{firebase_uid}` profile document, plus top-level `products`, `reference_images`, and `generated_posts` collections linked by `business_id`.

The intended product gives the owner a single dashboard that answers:

```text
What should I post today?
Why should I post it?
Can I generate and publish it now?
What worked recently?
What should I do next?
```

Primary users:

- Business owner
- Marketing operator
- Future: agency user managing multiple businesses

Initial business example from the idea:

- Millet or health food business
- Products such as Ragi Malt, Millet Chutney Powder, Millet Papad
- Content themes such as healthy breakfast, diabetes-friendly food, protein-rich breakfast, monsoon immunity, festival campaigns

## Tech Stack

Planned stack:

- Frontend: React, Vite, Material UI
- Authentication: Firebase Authentication
- Backend: FastAPI
- Agent orchestration: LangGraph
- Database: Firebase Firestore
- Storage: Firebase Storage
- Background work: scheduler or worker process
- Initial LLM providers: Gemini, OpenRouter, or Groq
- Initial image generation: Hugging Face FLUX through Inference Providers, Gemini image generation, or fallback SVG
- Video generation: later phase

Actual detected stack:

- Frontend: React, Vite, TypeScript, Material UI, lucide-react
- Backend: FastAPI, Pydantic Settings
- Agent orchestration: LangGraph dependency declared; `backend/app/graphs/daily_marketing_graph.py` currently runs a graph-boundary workflow that tries Gemini-backed content generation and falls back to deterministic local agents
- Database/storage/auth: Firebase frontend client initialization and Auth UI exist. Backend Firebase Admin token verification, business profile/product/generated-post Firestore persistence, and Firebase Storage uploads are implemented, but require service-account environment variables and `FIREBASE_STORAGE_BUCKET`.

## Repository Structure

Recommended project structure:

```text
ai-marketing-agent/
|-- frontend/
|   |-- src/
|   |   |-- app/
|   |   |-- components/
|   |   |-- pages/
|   |   |   |-- Dashboard/
|   |   |   |-- BusinessProfile/
|   |   |   |-- Products/
|   |   |   |-- ContentCalendar/
|   |   |   |-- GeneratedContent/
|   |   |   |-- Posters/
|   |   |   |-- Analytics/
|   |   |   |-- SEO/
|   |   |   |-- AgentLogs/
|   |   |   `-- Settings/
|   |   |-- services/
|   |   |-- hooks/
|   |   |-- lib/
|   |   `-- types/
|   |-- package.json
|   `-- vite.config.ts
|
|-- backend/
|   |-- app/
|   |   |-- main.py
|   |   |-- config.py
|   |   |-- api/
|   |   |-- agents/
|   |   |-- graphs/
|   |   |-- services/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- repositories/
|   |   `-- utils/
|   |-- requirements.txt
|   `-- Dockerfile
|
|-- docs/
|-- memory.md
|-- architecture.md
|-- routes.md
|-- api-map.md
|-- database-map.md
|-- dependency-graph.md
|-- .env.example
|-- README.md
`-- docker-compose.yml
```

Actual repository structure:

```text
S:\ai agent\
|-- .agents/
|-- .git/
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |-- agents/
|   |   |-- graphs/
|   |   |-- models/
|   |   |-- repositories/
|   |   |-- schemas/
|   |   |-- services/
|   |   |-- utils/
|   |   |-- config.py
|   |   `-- main.py
|   |-- README.md
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- app/
|   |   |-- lib/
|   |   |-- pages/
|   |   |-- services/
|   |   |-- main.tsx
|   |   `-- styles.css
|   |-- README.md
|   |-- package.json
|   |-- tsconfig.app.json
|   |-- tsconfig.json
|   |-- tsconfig.node.json
|   `-- vite.config.ts
|-- .env.example
|-- .gitignore
|-- README.md
|-- plan.md
|-- memory.md
|-- architecture.md
|-- routes.md
|-- api-map.md
|-- database-map.md
`-- dependency-graph.md
```

## System Architecture

Planned high-level architecture:

```text
Browser
  |
  v
React + Vite Frontend
  |
  v
FastAPI Backend
  |
  +--> LangGraph Agent Workflows
  |       |
  |       +--> LLM Provider
  |       +--> Image Generation Provider
  |       +--> Trend Sources
  |       +--> Social Publishing APIs
  |
  +--> Firebase Admin SDK
          |
          +--> Firebase Auth
          +--> Firestore
          `--> Firebase Storage
```

Primary agent workflow:

```text
Supervisor
  -> Business Knowledge Agent
  -> Trend Agent
  -> Product Selection Agent
  -> Content Strategy Agent
  -> Caption Agent
  -> Image Prompt Agent
  -> Poster Agent
  -> Calendar/Social Agent
  -> Analytics Agent
  -> Recommendation Agent
```

## Routing Map

No actual frontend routes exist yet.

Planned routes are documented in `routes.md`.

## Frontend Architecture

Planned frontend responsibilities:

- Authenticate users through Firebase Auth.
- Let users create and maintain business profiles.
- Let users manage products, benefits, pricing, images, audience, and brand tone.
- Display generated content and posters.
- Provide a content calendar.
- Show analytics and recommendations.
- Display agent logs for trust and debugging.

Planned frontend modules:

- Dashboard
- Business Profile
- Products
- Content Calendar
- Generated Content
- Posters
- Analytics
- SEO
- Social Media
- Agent Logs
- Settings

Actual frontend architecture:

- Entry point: `frontend/src/main.tsx`
- App shell: `frontend/src/app/App.tsx`
- Auth provider: `frontend/src/auth/AuthContext.tsx`
- Theme: `frontend/src/app/theme.ts`
- Firebase client: `frontend/src/lib/firebase.ts`
- Current page: `frontend/src/pages/Dashboard/DashboardPage.tsx`
- Login page: `frontend/src/pages/Login/LoginPage.tsx`
- Business profile page: `frontend/src/pages/BusinessProfile/BusinessProfilePage.tsx`
- Products page: `frontend/src/pages/Products/ProductsPage.tsx`
- Reference images page: `frontend/src/pages/ReferenceImages/ReferenceImagesPage.tsx`
- Generated content page: `frontend/src/pages/GeneratedContent/GeneratedContentPage.tsx`
- Content calendar page: `frontend/src/pages/ContentCalendar/ContentCalendarPage.tsx`
- API helper: `frontend/src/services/api.ts`
- The dashboard checks `GET /health` and displays API online/offline status.
- Firebase app/auth/firestore/storage/analytics clients are initialized from Vite environment variables.
- Firebase Auth UI/session flow is implemented with email/password sign in and sign up.
- React Router is not implemented yet; navigation is currently an in-app view switch.

## Backend Architecture

Planned backend responsibilities:

- Expose FastAPI endpoints.
- Verify Firebase Auth tokens.
- Run LangGraph workflows.
- Store and retrieve Firestore documents.
- Store generated assets in Firebase Storage.
- Schedule background jobs.
- Integrate with social media APIs.
- Log all agent decisions and outputs.

Actual backend architecture:

- Entry point: `backend/app/main.py`
- Settings: `backend/app/config.py`
- Routes:
  - `backend/app/api/routes_health.py`
  - `backend/app/api/routes_assets.py`
  - `backend/app/api/routes_agent.py`
  - `backend/app/api/routes_auth.py`
  - `backend/app/api/routes_business.py`
  - `backend/app/api/routes_products.py`
- Auth dependency:
  - `backend/app/dependencies.py`
- Schemas:
  - `backend/app/schemas/health.py`
  - `backend/app/schemas/agent.py`
- Placeholder graph:
  - `backend/app/graphs/daily_marketing_graph.py`
- Placeholder agent/service modules exist for the planned MVP agents and integrations.

## Database Architecture

Planned database: Firebase Firestore.

Planned collections:

- `users`
- `businesses`
- `products`
- `reference_images`
- `brand_profiles`
- `content_plans`
- `generated_posts`
- `generated_posters`
- `generated_videos`
- `seo_keywords`
- `competitors`
- `trends`
- `social_accounts`
- `scheduled_posts`
- `analytics`
- `sales`
- `recommendations`
- `agent_logs`

Detailed schema is documented in `database-map.md`.

Actual database implementation:

- Business profile, product, generated-post, and reference-image Firestore read/write exists in `backend/app/services/firebase_service.py`.
- Brand, reference, product, and generated poster images can be uploaded through `backend/app/services/storage_service.py` and stored in Firebase Storage.
- Firebase frontend environment variables exist in `.env.example`; local values are stored in ignored `frontend/.env.local`.
- `frontend/.env.example` documents the Vite Firebase variables used when running from the frontend directory.
- Backend Firebase Admin supports `FIREBASE_SERVICE_ACCOUNT_FILE` or inline `FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL`, and `FIREBASE_PRIVATE_KEY`.
- Backend Firebase token verification uses configurable `FIREBASE_TOKEN_CLOCK_SKEW_SECONDS`, defaulting to `10`, to tolerate small local clock drift.

## Authentication Flow

Planned authentication:

```text
User signs in with Firebase Auth
  |
  v
Frontend receives Firebase ID token
  |
  v
Frontend sends token to FastAPI in Authorization header
  |
  v
Backend verifies token with Firebase Admin SDK
  |
  v
Backend resolves user and business context
  |
  v
Protected API action runs
```

Actual authentication:

- Firebase frontend client initialization exists.
- Login UI and session handling are implemented through `frontend/src/auth/AuthContext.tsx`.
- Backend token verification is implemented in `backend/app/dependencies.py` and `backend/app/services/firebase_service.py`.
- Backend verification requires Firebase Admin service-account environment variables.
- Swagger UI is available at `/docs`; protected routes use FastAPI HTTP Bearer auth with Firebase ID tokens.

## API Inventory

Implemented APIs:

- `GET /health`
- `GET /me`
- `POST /assets/upload`
- `GET /business/profile`
- `POST /business/profile`
- `POST /products`
- `GET /products`
- `GET /products/{product_id}`
- `PATCH /products/{product_id}`
- `DELETE /products/{product_id}`
- `POST /reference-images`
- `GET /reference-images`
- `PATCH /reference-images/{reference_image_id}`
- `DELETE /reference-images/{reference_image_id}`
- `GET /content/posts`
- `GET /content/posts/{post_id}`
- `PATCH /content/posts/{post_id}`
- `DELETE /content/posts/{post_id}`
- `GET /schedule/posts`
- `POST /schedule/posts`
- `POST /schedule/recommend-time`
- `DELETE /schedule/posts/{scheduled_post_id}`
- `GET /posters`
- `POST /posters/generate`
- `POST /social/publish-now`
- `POST /agent/run-daily-plan`

Full API status is documented in `api-map.md`.

## Data Flow Diagrams

### Daily Marketing Content Flow

```text
Business owner opens dashboard
  |
  v
Frontend requests daily plan
  |
  v
FastAPI starts daily marketing graph
  |
  v
Business Knowledge Agent loads business, products, brand tone
  |
  v
Trend Agent loads trend signals
  |
  v
Product Selection Agent chooses product
  |
  v
Content Strategy Agent chooses content type
  |
  v
Caption Agent generates caption and hashtags
  |
  v
Prompt Agent creates poster prompt
  |
  v
Poster Agent generates image
  |
  v
Backend saves post, poster, and log records
  |
  v
Frontend shows content for approval
```

### Approval and Scheduling Flow

```text
User reviews generated content
  |
  v
User edits or approves
  |
  v
Frontend calls schedule API
  |
  v
Backend creates scheduled post
  |
  v
Scheduler publishes at selected time
  |
  v
Backend stores platform response and analytics seed record
```

## Environment Variables

Planned environment variables:

- `FIREBASE_PROJECT_ID`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_PRIVATE_KEY`
- `FIREBASE_STORAGE_BUCKET`
- `FIREBASE_TOKEN_CLOCK_SKEW_SECONDS`
- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_FIREBASE_STORAGE_BUCKET`
- `VITE_FIREBASE_MESSAGING_SENDER_ID`
- `VITE_FIREBASE_APP_ID`
- `VITE_FIREBASE_MEASUREMENT_ID`
- `LLM_PROVIDER`
- `GEMINI_MODEL`
- `GEMINI_API_KEY`
- `OPENROUTER_API_KEY`
- `GROQ_API_KEY`
- `IMAGE_API_KEY`
- `INSTAGRAM_CLIENT_ID`
- `INSTAGRAM_CLIENT_SECRET`
- `FACEBOOK_APP_ID`
- `FACEBOOK_APP_SECRET`
- `BACKEND_CORS_ORIGINS`

No secrets should be committed. Use `.env.example` with placeholder values only.

## Third Party Integrations

Planned integrations:

- Firebase Authentication
- Firestore
- Firebase Storage
- LLM provider: Gemini, OpenRouter, or Groq
- Image generation provider: `IMAGE_PROVIDER=huggingface`, `gemini`, or `fallback`
- Instagram/Facebook publishing APIs
- Future: Google Trends or approved trend data source
- Future: YouTube Shorts publishing
- Future: website SEO integrations

Actual integrations:

- Frontend Firebase client initialization exists for app, auth, Firestore, Storage, and Analytics.
- Backend Firebase Admin token verification and business profile Firestore access are implemented, but require service-account environment variables.
- Dependencies/config placeholders exist for LangGraph.
- Gemini Interactions API integration exists in the backend LLM service and is used only server-side when `LLM_PROVIDER=gemini` and `GEMINI_API_KEY` are configured. Daily content and schedule recommendations use low thinking to reduce token usage; fallback still happens when Gemini returns quota/rate-limit errors such as HTTP 429.

## Feature Inventory

### Business Memory

Purpose: store business profile, products, benefits, target audience, pricing, brand tone, and goals.

Status: business profile, brand kit, uploaded brand logo/avatar URLs, product memory, uploaded product image galleries, and labelled uploaded reference image memory implemented. This memory is now actively passed into content generation, poster prompt generation, and final poster composition.
Compatibility note: older Firestore business/product documents are normalized with default Phase 11 fields on read so existing users do not crash the frontend.

### Daily Content Generation

Purpose: generate one practical daily content package containing product, trend, strategy, caption, hashtags, image prompt, and poster.

Status: Gemini-backed daily generation is implemented with deterministic fallback. Generated posts are saved for review. Content review can edit, approve, reject/delete generated drafts, and generate poster images through Hugging Face FLUX, Gemini, or fallback SVG. Approved drafts can be scheduled into the manual content calendar, with Gemini/fallback schedule time recommendations.

### Poster Generation

Purpose: convert product and campaign idea into a commercial poster.

Status: Hugging Face FLUX/Gemini/fallback poster generation is implemented. Generated raster posters are uploaded to Firebase Storage when configured and stamped with the uploaded brand logo at the top when `brand_kit.logo_url` exists. If product images exist, the first uploaded product image is composited into the final raster poster so the output carries real product identity. Local `/static/posters` output remains only as a fallback if Storage upload fails.

### Content Calendar

Purpose: organize generated posts into 7-day and 30-day plans.

Status: manual calendar scheduling plus AI schedule time recommendation is implemented.

### Social Publishing

Purpose: publish or schedule approved content to social platforms.

Status: mock publishing is implemented. `POST /social/publish-now` marks scheduled content and the source generated post as `published`, stores a mock platform post id, and leaves real Meta/Instagram publishing for the next integration phase.

### SEO

Purpose: generate keywords, blog topics, meta titles, descriptions, and FAQs.

Status: planned after MVP.

### Analytics

Purpose: measure reach, likes, comments, shares, saves, CTR, and content performance by type.

Status: planned after publishing integration.

### Sales Intelligence

Purpose: connect content campaigns to orders or sales outcomes.

Status: planned later.

### Recommendations

Purpose: tell the owner what to do next based on trend, analytics, product, and sales signals.

Status: planned after analytics.

## Dependency Graph

No actual source-level dependency graph exists yet.

Planned module dependency graph is documented in `dependency-graph.md`.

## Important Files

Current important files:

- `plam.md`: original planning note generated from the AI Marketing Partner idea.
- `memory.md`: permanent project brain and implementation context.
- `architecture.md`: architecture decisions and system map.
- `routes.md`: frontend and backend route inventory.
- `api-map.md`: API contract inventory.
- `database-map.md`: Firestore and storage schema.
- `dependency-graph.md`: module dependency map and high-impact files.

## Performance Notes

Known future performance concerns:

- Avoid running every agent for every page load.
- Cache business memory and trend results.
- Run image generation asynchronously.
- Do not block the dashboard while posters/videos generate.
- Store agent outputs so users can reuse and edit them.
- Use paginated analytics and logs.
- Keep Firestore reads predictable by business ID and date range.

## Technical Debt

Current debt:

- Firebase Admin credentials are not present in the workspace, so protected backend routes need `FIREBASE_SERVICE_ACCOUNT_FILE` or inline service-account environment setup before runtime testing.
- Firebase Authentication must be initialized in Firebase Console and Email/Password sign-in must be enabled before the frontend login screen can create accounts.
- LangGraph dependency is declared, but the daily graph is currently a graph-boundary function rather than full LangGraph nodes.
- Frontend routing is not implemented yet.
- Backend dependencies were installed in the local virtualenv for this work session, including `python-multipart` for file uploads.
- Local verification found Python available, but Node/npm are not on PATH.
- Local global Python has an incompatible FastAPI/Starlette pairing; use a clean backend virtualenv from `backend/requirements.txt`.
- Git repository state is invalid according to `git status`.

Future risks:

- Over-splitting into too many agents too early.
- Auto-posting before approval, which could create brand risk.
- Weak logs, making AI decisions hard to trust.
- Poor schema design around multi-business support.
- Depending on unstable unofficial trend sources.

## Development Workflow

Recommended workflow:

1. Update docs before or during feature design.
2. Implement backend contract and schema.
3. Implement frontend workflow.
4. Add logs for agent actions.
5. Run tests and smoke-test the UI.
6. Update the matching docs before finishing the task.

## Deployment Process

Planned deployment:

- Frontend: Vercel, Firebase Hosting, or similar static hosting.
- Backend: Render, Railway, Fly.io, Cloud Run, or container hosting.
- Database/storage/auth: Firebase.

Actual deployment:

- UNKNOWN - NEEDS VERIFICATION.

## Known Risks

- Social platform APIs require app review and permissions.
- Video generation may be expensive and slow.
- Trend data may require paid or approved sources.
- LLM output needs moderation and brand review.
- Generated images may need logo, product, and claim validation.
- Health food claims must be reviewed carefully to avoid misleading medical claims.

## Future Recommendations

Build in this order:

1. Project scaffold.
2. Firebase Auth and business profile.
3. Product management.
4. Daily content generation graph. First deterministic version is implemented.
5. Manual approval and generated content review. Current review version is implemented.
6. Gemini-backed content generation. Current Gemini/fallback version is implemented.
7. Content calendar and scheduling. Current manual scheduling version is implemented.
8. AI schedule time recommendation. Current Gemini/fallback recommendation version is implemented.
9. Poster generation. Current Hugging Face FLUX/Gemini/fallback image version is implemented.
10. Social publishing foundation. Current mock publish version is implemented.
11. Brand kit and visual memory foundation. Current upload-backed visual memory version is implemented.
12. Firebase Storage uploads for brand/reference/product/generated poster assets. Current upload foundation is implemented.
13. Brand-grounded generation using brand kit, product images, and reference images. Current prompt and final composition foundation is implemented.
14. Use uploaded reference/product images as true image-conditioning inputs for the image model where provider support allows it.
15. Analytics.
16. Recommendations.
17. SEO and blogs.
18. Reels/video generation.

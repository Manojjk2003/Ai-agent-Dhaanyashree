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

Current repository state: Phase 1 foundation scaffold exists. The workspace now contains a React/Vite frontend skeleton, a FastAPI backend skeleton, a placeholder LangGraph workflow location, root environment/ignore/readme files, and project memory documents.

Verified from repository: `git status` reports this is not a valid Git repository, even though a `.git` entry is present in the workspace.

## Business Purpose

The business problem is that small business owners need consistent marketing but often lack time, strategy, design capability, SEO knowledge, trend awareness, and analytics discipline.

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
- Initial image generation: external image-generation API
- Video generation: later phase

Actual detected stack:

- Frontend: React, Vite, TypeScript, Material UI, lucide-react
- Backend: FastAPI, Pydantic Settings
- Agent orchestration: LangGraph dependency declared; workflow implementation is currently a placeholder in `backend/app/graphs/daily_marketing_graph.py`
- Database/storage/auth: Firebase dependencies/config placeholders only; no implementation yet

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
- Theme: `frontend/src/app/theme.ts`
- Current page: `frontend/src/pages/Dashboard/DashboardPage.tsx`
- API helper: `frontend/src/services/api.ts`
- The dashboard checks `GET /health` and displays API online/offline status.
- Routing and Firebase Auth are not implemented yet.

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
  - `backend/app/api/routes_agent.py`
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

- No Firestore repository implementation exists yet.
- Firebase environment placeholders exist in `.env.example`.
- `backend/app/services/firebase_service.py` exists as a placeholder.

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

- Not implemented yet.
- Firebase client/admin config placeholders exist only.

## API Inventory

Implemented APIs:

- `GET /health`
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
- `LLM_PROVIDER`
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
- Image generation provider
- Instagram/Facebook publishing APIs
- Future: Google Trends or approved trend data source
- Future: YouTube Shorts publishing
- Future: website SEO integrations

Actual integrations:

- No live third-party integration is implemented yet.
- Dependencies/config placeholders exist for LangGraph and Firebase.

## Feature Inventory

### Business Memory

Purpose: store business profile, products, benefits, target audience, pricing, brand tone, and goals.

Status: planned.

### Daily Content Generation

Purpose: generate one practical daily content package containing product, trend, strategy, caption, hashtags, image prompt, and poster.

Status: planned MVP.

### Poster Generation

Purpose: convert product and campaign idea into a commercial poster.

Status: planned MVP.

### Content Calendar

Purpose: organize generated posts into 7-day and 30-day plans.

Status: planned MVP.

### Social Publishing

Purpose: publish or schedule approved content to social platforms.

Status: planned after manual approval flow.

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

- Firebase Auth is not implemented yet.
- Firestore repositories are not implemented yet.
- LangGraph dependency is declared, but the daily graph is currently a placeholder function.
- Frontend routing is not implemented yet.
- Dependencies have not been installed in this work session.
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
4. Daily content generation graph.
5. Poster generation.
6. Manual approval and content calendar.
7. Social scheduling.
8. Analytics.
9. Recommendations.
10. SEO and blogs.
11. Reels/video generation.

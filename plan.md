## Phase 10 Setup Status

Status: mock social publishing foundation created.

Created:

- `backend/app/api/routes_social.py` protected social publishing API.
- `backend/app/services/social_service.py` mock publisher adapter boundary.
- `POST /social/publish-now` for scheduled posts.
- Scheduled post publish metadata: `published_at`, `platform_post_id`, and `error_message`.
- Firestore workflow that marks `scheduled_posts/{scheduledPostId}` and the source `generated_posts/{postId}` as `published`.
- Calendar UI **Publish Now** action for scheduled posts.
- Calendar UI published timestamp, mock platform post id, and publish error display.

Implemented backend routes:

- `POST /social/publish-now`.

Publishing workflow:

```text
Content tab
  -> Approve generated content
  -> Calendar tab
  -> Schedule approved post
  -> Publish Now
  -> Mock social publisher returns platform_post_id
  -> scheduled_posts and generated_posts are marked published
```

Next phase:

- Connect real Meta/Instagram/Facebook publishing credentials.
- Add social account connection records.
- Move from manual publish button to background scheduled publishing.

## Phase 9 Setup Status

Status: poster image generation created and Hugging Face FLUX provider support added.

Created:

- `backend/app/schemas/generated_poster.py` generated poster schemas.
- `backend/app/api/routes_posters.py` protected poster APIs.
- `backend/app/services/image_service.py` Hugging Face FLUX, Gemini image generation, plus fallback SVG poster generation.
- Static poster serving from repo-level `generated/posters` through `/static/posters`.
- Firestore generated poster metadata in top-level `generated_posters/{posterId}` documents linked by `business_id`.
- Content Review **Generate Poster** button.
- Content Review poster preview for the selected generated post.

Implemented backend routes:

- `GET /posters`.
- `POST /posters/generate`.

Poster workflow:

```text
Content tab
  -> Edit or approve generated content
  -> Generate Poster
  -> Hugging Face FLUX or Gemini image model creates poster, or fallback SVG is created
  -> Save poster metadata to generated_posters
  -> Preview poster in Content Review
```

Provider setup:

```text
IMAGE_PROVIDER=huggingface
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell
HF_TOKEN=<your-hugging-face-token>
```

Next phase:

- Mock social publishing foundation. Implemented in Phase 10.
- Later move poster binary storage from local `generated/posters` to Firebase Storage.

## Phase 8 Setup Status

Status: AI schedule time recommendation created.

Created:

- `POST /schedule/recommend-time` protected API.
- Gemini-backed schedule recommendation using business profile, product memory, generated content, target date, and platform.
- Heuristic fallback recommendation when Gemini is unavailable.
- Recommendation response with `recommended_at`, `reason`, `confidence`, `alternative_slots`, and `generation_source`.
- Calendar UI **Recommend Time** button.
- Calendar UI applies the recommended time to the schedule input while still allowing manual edits before saving.

Implemented backend routes:

- `POST /schedule/recommend-time`.

Recommendation workflow:

```text
Calendar tab
  -> Choose approved content
  -> Click Recommend Time
  -> Gemini/fallback suggests best time and alternatives
  -> User accepts or edits time
  -> Schedule selected post
```

Next phase:

- Poster image generation. Implemented in Phase 9.
- Later connect scheduled posts to real social publishing APIs.

## Phase 7 Setup Status

Status: manual content calendar and scheduling created.

Created:

- `backend/app/schemas/scheduled_post.py` scheduled post schemas.
- `backend/app/api/routes_schedule.py` protected schedule APIs.
- Firestore scheduled post storage in top-level `scheduled_posts/{scheduledPostId}` documents linked by `business_id`.
- Scheduling workflow that requires generated content to be `approved`.
- Creating a scheduled post updates the source generated post to `scheduled`.
- Cancelling a scheduled post deletes the schedule document and returns the source generated post to `approved`.
- `frontend/src/pages/ContentCalendar/ContentCalendarPage.tsx` calendar/schedule UI.
- Calendar navigation in the protected app shell.
- Scheduled content API helpers in `frontend/src/services/api.ts`.

Implemented backend routes:

- `GET /schedule/posts`.
- `POST /schedule/posts`.
- `DELETE /schedule/posts/{scheduled_post_id}`.

Calendar workflow:

```text
Content tab
  -> Approve generated content
  -> Calendar tab
  -> Choose approved content
  -> Pick schedule date/time
  -> Save to scheduled_posts
```

Next phase:

- Add poster image generation for approved or scheduled content.
- Later connect scheduled posts to real social publishing APIs.

## Phase 6 Setup Status

Status: Gemini-backed daily marketing generation added with fallback.

Created:

- `backend/app/services/llm_service.py` Gemini Interactions API integration.
- Daily graph now tries Gemini using business profile plus selected product memory.
- Deterministic caption/hashtag/poster prompt generation remains as fallback when Gemini is not configured, the key is rejected, the network fails, or Gemini returns invalid JSON.
- `generation_source` added to daily plan and generated post responses.
- Dashboard and content review UI show whether output came from Gemini or fallback rules.

Environment:

```text
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-3.5-flash
GEMINI_API_KEY=<your-google-ai-studio-key>
```

Generate or view the key at:

```text
https://aistudio.google.com/api-keys
```

Next phase:

- Add content calendar and scheduling for approved generated posts.
- Add poster image generation for approved content.

## Phase 5 Setup Status

Status: generated content persistence and review created.

Created:

- `backend/app/schemas/generated_post.py` generated post schemas.
- `backend/app/api/routes_content.py` protected generated content APIs.
- Firestore generated post storage in top-level `generated_posts/{postId}` documents linked by `business_id`.
- Daily marketing workflow now saves generated content automatically.
- `frontend/src/pages/GeneratedContent/GeneratedContentPage.tsx` content review UI.
- Content navigation in the protected app shell.
- Generated content API helpers in `frontend/src/services/api.ts`.

Implemented backend routes:

- `GET /content/posts`.
- `GET /content/posts/{post_id}`.
- `PATCH /content/posts/{post_id}`.
- `DELETE /content/posts/{post_id}`.

Review workflow:

```text
Generate Today
  -> Save generated post
  -> Content tab
  -> Edit caption / hashtags / poster prompt
  -> Approve or reject/delete
```

Next phase:

- Add content calendar.
- Schedule approved posts.
- Add poster image generation for approved content.
## Phase 4 Setup Status

Status: first daily marketing workflow created.

Business model decision:

```text
User account
  -> One business profile
      -> Many products
```

Created:

- Deterministic product selection agent.
- Deterministic content strategy agent.
- Deterministic caption/hashtag agent.
- Deterministic poster prompt agent.
- Protected `POST /agent/run-daily-plan` using Firebase token auth.
- Daily plan response with selected product, reason, content type, idea, caption, hashtags, and poster prompt.
- Dashboard Generate Today action and generated plan panel.
- UI wording updated around one business profile with many products.

Next phase:

- Save generated plans/posts into Firestore.
- Add content review/calendar.
- Later replace deterministic generation with LLM-backed LangGraph nodes.
## Phase 3 Setup Status

Status: product memory foundation created.

Created:

- `backend/app/schemas/product.py` product request/response schemas.
- `backend/app/api/routes_products.py` protected product CRUD APIs.
- Firestore product storage in top-level `products/{productId}` documents linked by `business_id`.
- `frontend/src/pages/Products/ProductsPage.tsx` product management UI.
- Frontend product API helpers in `frontend/src/services/api.ts`.
- Products navigation in the protected app shell.
- Dashboard product memory count.

Implemented backend routes:

- `POST /products`.
- `GET /products`.
- `GET /products/{product_id}`.
- `PATCH /products/{product_id}`.
- `DELETE /products/{product_id}`.

Requirements before live runtime:

- Firebase Admin service-account values must be present in backend `.env`.
- Firestore must be enabled in Firebase Console.

Next phase:

- Wire business profile + products into the first real LangGraph daily marketing workflow.
- Generate product selection, content idea, caption, hashtags, and poster prompt.
## Phase 2 Setup Status

Status: Firebase Auth and business profile foundation created.

Created:

- `frontend/src/auth/AuthContext.tsx` Firebase Auth session provider.
- `frontend/src/pages/Login/LoginPage.tsx` email/password login and sign-up UI.
- `frontend/src/pages/BusinessProfile/BusinessProfilePage.tsx` business memory form.
- Backend Firebase token verification dependency.
- `GET /me`.
- `GET /business/profile`.
- `POST /business/profile`.

Requirements before live runtime:

- Enable Email/Password provider in Firebase Authentication.
- Add Firebase Admin service-account values to backend `.env`.
- Install frontend and backend dependencies.

Next phase:

- Product management.
- Use business profile and products inside the LangGraph daily marketing workflow.

## Phase 1 Setup Status

Status: foundation scaffold created.

Created:

- `backend/` FastAPI application skeleton.
- `backend/app/graphs/` LangGraph workflow location with a placeholder daily marketing graph.
- `backend/app/agents/` placeholder MVP agent modules.
- `backend/app/services/` placeholder integration modules.
- `frontend/` React + Vite + Material UI dashboard skeleton.
- `frontend/src/lib/firebase.ts` Firebase Web SDK initialization.
- Root `.env.example`, `.gitignore`, and `README.md`.

Implemented initial backend routes:

- `GET /health`
- `POST /agent/run-daily-plan`

Next phase:

- Install dependencies.
- Run backend and frontend locally.
- Add Firebase Auth and business profile storage.
- Add product management.
- Replace the daily graph placeholder with real business-memory and content-generation steps.

Your idea is strong, but I would not build it as 16 separate â€œagentsâ€ from day one. I would build it as an **AI Marketing Operating System** where the business owner gives business data, and the system repeatedly plans, creates, publishes, measures, and improves content.

The core loop should be:

```text
Business Data
   -> Trend + Product Decision
   -> Content Strategy
   -> Caption / Poster / Reel Script
   -> Review or Auto-Publish
   -> Analytics
   -> Recommendation
   -> Next Content Plan
```

The important thing: this should not feel like â€œmany random AI tools.â€ It should feel like **one marketing partner** that remembers the business and improves every week.

---

## My Suggested Architecture

I would divide the system into 4 main layers:

```text
Frontend Dashboard
Backend API
Agent Orchestration
Data + Storage
```

### 1. Frontend

Use:

```text
React
Vite
Material UI
Firebase Auth
```

Main screens:

```text
Dashboard
Business Profile
Products
Content Calendar
Content Generator
Posters
SEO
Social Media
Analytics
Recommendations
Agent Logs
Settings
```

The dashboard should show:

```text
Today's suggested product
Today's trend
Generated caption
Generated poster
Scheduled posts
Recent performance
Next recommendation
```

---

### 2. Backend

Use:

```text
FastAPI
LangGraph
Firebase Admin SDK
Background scheduler
```

Backend responsibilities:

```text
Handle API requests
Run agent workflows
Save generated outputs
Schedule daily jobs
Connect to social platforms
Store logs
```

Example endpoints:

```text
POST /business/profile
POST /products
POST /agent/run-daily-plan
POST /content/generate
POST /posters/generate
POST /social/schedule
GET  /analytics
GET  /recommendations
GET  /agent/logs
```

---

## Agent Design

Instead of starting with 16 independent agents, I would group them into **workflows**.

### MVP Workflow

```text
Supervisor Agent
   -> Business Knowledge Agent
   -> Trend Agent
   -> Product Selection Agent
   -> Content Strategy Agent
   -> Caption Agent
   -> Image Prompt Agent
   -> Poster Agent
   -> Calendar/Social Agent
```

This is enough for a useful first version.

The MVP user flow:

```text
Business owner adds products
Business owner adds brand tone and audience
System finds a trend
System chooses product
System creates caption and poster
Business owner approves
System schedules or posts
```

---

## Data Collections

Firestore structure could look like this:

```text
users
businesses
products
brand_profiles
content_plans
generated_posts
generated_posters
generated_videos
seo_keywords
competitors
trends
social_accounts
scheduled_posts
analytics
sales
recommendations
agent_logs
```

Keep `businesses` as a top-level collection, but the MVP uses one business profile per signed-in user. Products and generated posts are separate top-level collections linked with `business_id`.

Example:

```text
businesses/{firebase_uid}
products/{productId}
content_plans/{planId}
generated_posts/{postId}
agent_logs/{logId}
```

Storage:

```text
posters/
videos/
blogs/
product-images/
brand-assets/
```

---

## Recommended Folder Structure

```text
ai-marketing-agent/
â”‚
â”œâ”€â”€ frontend/
â”‚   â”œâ”€â”€ src/
â”‚   â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ components/
â”‚   â”‚   â”œâ”€â”€ pages/
â”‚   â”‚   â”‚   â”œâ”€â”€ Dashboard/
â”‚   â”‚   â”‚   â”œâ”€â”€ Products/
â”‚   â”‚   â”‚   â”œâ”€â”€ ContentCalendar/
â”‚   â”‚   â”‚   â”œâ”€â”€ GeneratedContent/
â”‚   â”‚   â”‚   â”œâ”€â”€ Posters/
â”‚   â”‚   â”‚   â”œâ”€â”€ Analytics/
â”‚   â”‚   â”‚   â”œâ”€â”€ SEO/
â”‚   â”‚   â”‚   â”œâ”€â”€ AgentLogs/
â”‚   â”‚   â”‚   â””â”€â”€ Settings/
â”‚   â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ hooks/
â”‚   â”‚   â”œâ”€â”€ lib/
â”‚   â”‚   â””â”€â”€ types/
â”‚   â”‚
â”‚   â”œâ”€â”€ package.json
â”‚   â””â”€â”€ vite.config.ts
â”‚
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ main.py
â”‚   â”‚   â”œâ”€â”€ config.py
â”‚   â”‚   â”œâ”€â”€ api/
â”‚   â”‚   â”‚   â”œâ”€â”€ routes_business.py
â”‚   â”‚   â”‚   â”œâ”€â”€ routes_products.py
â”‚   â”‚   â”‚   â”œâ”€â”€ routes_content.py
â”‚   â”‚   â”‚   â”œâ”€â”€ routes_social.py
â”‚   â”‚   â”‚   â””â”€â”€ routes_analytics.py
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ agents/
â”‚   â”‚   â”‚   â”œâ”€â”€ supervisor.py
â”‚   â”‚   â”‚   â”œâ”€â”€ business_knowledge.py
â”‚   â”‚   â”‚   â”œâ”€â”€ trend_agent.py
â”‚   â”‚   â”‚   â”œâ”€â”€ product_selector.py
â”‚   â”‚   â”‚   â”œâ”€â”€ content_strategy.py
â”‚   â”‚   â”‚   â”œâ”€â”€ caption_agent.py
â”‚   â”‚   â”‚   â”œâ”€â”€ prompt_agent.py
â”‚   â”‚   â”‚   â”œâ”€â”€ poster_agent.py
â”‚   â”‚   â”‚   â”œâ”€â”€ seo_agent.py
â”‚   â”‚   â”‚   â”œâ”€â”€ analytics_agent.py
â”‚   â”‚   â”‚   â””â”€â”€ recommendation_agent.py
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ graphs/
â”‚   â”‚   â”‚   â”œâ”€â”€ daily_marketing_graph.py
â”‚   â”‚   â”‚   â””â”€â”€ seo_graph.py
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”‚   â”œâ”€â”€ firebase_service.py
â”‚   â”‚   â”‚   â”œâ”€â”€ llm_service.py
â”‚   â”‚   â”‚   â”œâ”€â”€ image_service.py
â”‚   â”‚   â”‚   â”œâ”€â”€ social_service.py
â”‚   â”‚   â”‚   â””â”€â”€ scheduler_service.py
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ schemas/
â”‚   â”‚   â”œâ”€â”€ repositories/
â”‚   â”‚   â””â”€â”€ utils/
â”‚   â”‚
â”‚   â”œâ”€â”€ requirements.txt
â”‚   â””â”€â”€ Dockerfile
â”‚
â”œâ”€â”€ docs/
â”‚   â”œâ”€â”€ architecture.md
â”‚   â”œâ”€â”€ agent-flow.md
â”‚   â””â”€â”€ firebase-schema.md
â”‚
â”œâ”€â”€ .env.example
â”œâ”€â”€ README.md
â””â”€â”€ docker-compose.yml
```

---

## MVP Phases

### Phase 1: Business Memory

Build:

```text
Auth
Business profile
Products
Brand tone
Target audience
Firestore storage
```

This gives the agent memory.

### Phase 2: Daily Content Generator

Build:

```text
Trend Agent
Product Selection Agent
Content Strategy Agent
Caption Agent
Prompt Agent
Poster Agent
```

Output:

```text
Product to promote
Content idea
Caption
Hashtags
Poster prompt
Generated poster
```

### Phase 3: Calendar + Approval

Build:

```text
7-day content calendar
Manual approve/reject
Edit caption
Edit poster prompt
Schedule post
```

Do manual approval first. Auto-posting can come later.

### Phase 4: Social Posting

Add:

```text
Instagram
Facebook
YouTube Shorts later
LinkedIn later
```

Start with one platform, probably Instagram/Facebook.

### Phase 5: Analytics + Recommendations

Add:

```text
Post performance
Best product
Best content type
Best posting time
Agent recommendations
```

---

## My Main Advice

Do not build â€œall agentsâ€ first. Build **one powerful daily marketing workflow**.

Your first successful version should do this:

```text
Every morning:
1. Read business data
2. Pick one product
3. Pick one trend
4. Generate one content idea
5. Generate caption
6. Generate poster
7. Save to calendar
8. Ask owner to approve
```

That alone is valuable.

After that, add SEO, reels, analytics, and sales intelligence.

The real product is not â€œAI agents.â€ The real product is:

```text
A business owner opens the dashboard and sees:
"What should I post today, why, and can I publish it now?"
```

That is the sharp MVP.

You mean **LangGraph**.

LangGraph is a Python library used to build **agent workflows** as a graph.

In your project:

```text
FastAPI = backend API server
LangGraph = brain/workflow engine inside backend
React = frontend dashboard
Firebase = auth/database/storage
```

Example:

```text
User clicks "Generate Today's Post"
        |
        v
React calls FastAPI API
        |
        v
FastAPI runs LangGraph workflow
        |
        v
LangGraph calls agents one by one:
Trend Agent
Product Agent
Caption Agent
Poster Agent
        |
        v
FastAPI saves result to Firebase
        |
        v
React shows result
```

So LangGraph should stay inside:

```text
backend/app/graphs/
```

Example files:

```text
backend/
â””â”€â”€ app/
    â”œâ”€â”€ main.py
    â”œâ”€â”€ api/
    â”œâ”€â”€ agents/
    â”‚   â”œâ”€â”€ trend_agent.py
    â”‚   â”œâ”€â”€ product_selector.py
    â”‚   â”œâ”€â”€ caption_agent.py
    â”‚   â””â”€â”€ poster_agent.py
    â””â”€â”€ graphs/
        â””â”€â”€ daily_marketing_graph.py
```

Think of it like this:

```text
FastAPI receives the request.
LangGraph decides the agent flow.
Agents do each task.
```

So yes: **LangGraph belongs in the backend folder with FastAPI.**


Next practical step is installing tools/dependencies, then running:
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload


Node.js is installed:
cd frontend
npm install
npm run dev




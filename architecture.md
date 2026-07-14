# Architecture

## Documentation Maintenance Rule

Update this file whenever system boundaries, services, agents, deployment shape, third-party integrations, or major data flows change. Also update `memory.md` when the change affects project understanding.

## Current State

Phase 3 foundation scaffold exists. The frontend initializes Firebase, supports email/password sign in/sign up, gates the app by auth state, and includes business profile and product management forms. The backend has health, current-user, business profile, product, and daily-plan routes. Firebase Admin verification and Firestore business/product persistence are implemented, but require service-account environment variables to run.

## Intended System Map

```text
Browser
  |
  v
React + Vite + Material UI
  |
  +--> Firebase Web SDK: initialized
  |
  | HTTPS + Firebase ID token
  v
FastAPI Backend
  |
  +--> Auth Middleware
  |       `--> Firebase Admin SDK
  |
  +--> API Routes
  |       +--> Health API: implemented
  |       +--> Auth API: implemented
  |       +--> Business/Profile APIs: implemented
  |       +--> Product APIs: implemented
  |       +--> Daily Plan API: scaffolded
  |       +--> Product APIs: planned
  |       +--> Content APIs: planned
  |       +--> Poster APIs: planned
  |       +--> Social APIs: planned
  |       +--> Analytics APIs: planned
  |       `--> Agent Log APIs: planned
  |
  +--> LangGraph Workflows
  |       +--> Daily Marketing Graph: placeholder
  |       +--> SEO Graph
  |       +--> Analytics Recommendation Graph
  |       `--> Future Video Graph
  |
  +--> Services
  |       +--> LLM Service: placeholder
  |       +--> Image Service: placeholder
  |       +--> Firebase Service: placeholder
  |       +--> Social Service: placeholder
  |       `--> Scheduler Service: placeholder
  |
  v
Firebase
  +--> Auth
  +--> Firestore
  +--> Storage
  `--> Analytics
```

## Agent Architecture

The product should expose one marketing partner experience, but internally it can use specialized agents.

### Supervisor Agent

Responsibilities:

- Decide the workflow for a requested goal.
- Load business context.
- Call specialized agents in order.
- Validate that required output exists.
- Save agent logs.
- Return user-facing recommendations.

### Business Knowledge Agent

Responsibilities:

- Read business profile, products, audience, pricing, brand tone, and goals.
- Summarize long-term business memory.
- Provide context to other agents.

### Trend Agent

Responsibilities:

- Identify relevant current or seasonal themes.
- Score trends by relevance to the business.
- Save trend records.

### Product Selection Agent

Responsibilities:

- Choose which product to promote.
- Use trends, inventory, sales signals, and recent content history.

### Content Strategy Agent

Responsibilities:

- Choose content type.
- Examples: educational post, recipe post, health tip, festival post, customer story, product promotion.

### Caption Agent

Responsibilities:

- Generate caption, CTA, and hashtags.
- Keep tone consistent with brand profile.

### Image Prompt Agent

Responsibilities:

- Convert strategy into a high-quality image generation prompt.
- Include product, context, style, audience, and commercial constraints.

### Poster Agent

Responsibilities:

- Call image generation provider.
- Store output in Firebase Storage.
- Save metadata in Firestore.

### Social Media Agent

Responsibilities:

- Schedule or publish approved posts.
- Store platform responses.
- Support Instagram/Facebook first.

### Analytics Agent

Responsibilities:

- Collect performance data.
- Normalize metrics across platforms.
- Save analytics records.

### Recommendation Agent

Responsibilities:

- Convert trend, sales, and analytics signals into next actions.

## Primary MVP Flow

```text
Daily scheduler or user action
  |
  v
POST /agent/run-daily-plan
  |
  v
Supervisor loads business context
  |
  v
Trend Agent finds topic
  |
  v
Product Selection Agent chooses product
  |
  v
Content Strategy Agent chooses content format
  |
  v
Caption Agent creates caption/CTA/hashtags
  |
  v
Image Prompt Agent creates visual prompt
  |
  v
Poster Agent generates image
  |
  v
Firestore + Storage save result
  |
  v
Frontend displays post for approval
```

Current scaffold behavior:

```text
Frontend dashboard
  |
  +--> Initializes Firebase web client
  |
  v
GET /health
  |
  v
FastAPI returns service status
```

```text
Client
  |
  v
POST /agent/run-daily-plan
  |
  v
FastAPI calls placeholder daily marketing graph
  |
  v
Backend returns generated placeholder IDs and ready_for_review status
```

## Background Jobs

Planned jobs:

- Daily plan generation.
- Scheduled publishing.
- Analytics refresh.
- Trend refresh.

Implementation options:

- Simple scheduler inside backend for MVP.
- Dedicated worker later if the workload grows.

## External Services

Planned:

- Firebase Auth
- Firestore
- Firebase Storage
- LLM provider
- Image generation provider
- Instagram/Facebook APIs

Future:

- Google Trends or other trend source
- YouTube Shorts API
- Ecommerce or POS sales integration

## Architecture Decisions

- Use manual approval before social publishing in MVP.
- Use one daily marketing workflow before building all advanced agents.
- Keep agent logs as first-class data so outputs are inspectable.
- Use `businessId` as the main partition key for multi-business support.
- Store generated assets in Firebase Storage and metadata in Firestore.

## Unknowns

- Final LLM provider.
- Final image generation provider.
- Final hosting provider.
- Social platform permission status.
- Whether the project will support multiple businesses per user in MVP.

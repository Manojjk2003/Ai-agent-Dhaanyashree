# Dependency Graph

## Documentation Maintenance Rule

Update this file whenever important modules are added, removed, renamed, or their dependencies change. If a dependency changes architecture or data flow, update `architecture.md` and `memory.md`.

## Current State

Phase 14 source files exist. This file tracks the current scaffold graph and the intended module dependency graph.

## Current Backend Dependency Graph

```text
backend/app/main.py
  -> backend/app/config.py
  -> backend/app/api/routes_health.py
  -> backend/app/api/routes_auth.py
  -> backend/app/api/routes_assets.py
  -> backend/app/api/routes_business.py
  -> backend/app/api/routes_content.py
  -> backend/app/api/routes_products.py
  -> backend/app/api/routes_reference_images.py
  -> backend/app/api/routes_schedule.py
  -> backend/app/api/routes_posters.py
  -> backend/app/api/routes_social.py
  -> backend/app/api/routes_agent.py

backend/app/api/routes_health.py
  -> backend/app/schemas/health.py

backend/app/api/routes_auth.py
  -> backend/app/dependencies.py
  -> backend/app/schemas/auth.py

backend/app/api/routes_assets.py
  -> backend/app/dependencies.py
  -> backend/app/schemas/asset.py
  -> backend/app/schemas/auth.py
  -> backend/app/services/storage_service.py

backend/app/api/routes_business.py
  -> backend/app/dependencies.py
  -> backend/app/schemas/auth.py
  -> backend/app/schemas/business.py
  -> backend/app/services/firebase_service.py

backend/app/api/routes_products.py
  -> backend/app/dependencies.py
  -> backend/app/schemas/auth.py
  -> backend/app/schemas/product.py
  -> backend/app/services/firebase_service.py

backend/app/api/routes_reference_images.py
  -> backend/app/dependencies.py
  -> backend/app/schemas/auth.py
  -> backend/app/schemas/reference_image.py
  -> backend/app/services/firebase_service.py

backend/app/api/routes_content.py
  -> backend/app/dependencies.py
  -> backend/app/schemas/auth.py
  -> backend/app/schemas/generated_post.py
  -> backend/app/services/firebase_service.py

backend/app/api/routes_schedule.py
  -> backend/app/dependencies.py
  -> backend/app/schemas/auth.py
  -> backend/app/schemas/scheduled_post.py
  -> backend/app/services/firebase_service.py
  -> backend/app/services/llm_service.py

backend/app/api/routes_posters.py
  -> backend/app/dependencies.py
  -> backend/app/schemas/auth.py
  -> backend/app/schemas/generated_poster.py
  -> backend/app/services/firebase_service.py
  -> backend/app/services/image_service.py
  -> loads business/product/reference visual memory for poster composition

backend/app/api/routes_social.py
  -> backend/app/dependencies.py
  -> backend/app/schemas/auth.py
  -> backend/app/schemas/scheduled_post.py
  -> backend/app/services/firebase_service.py
  -> backend/app/services/social_service.py

backend/app/api/routes_agent.py
  -> backend/app/dependencies.py
  -> backend/app/graphs/daily_marketing_graph.py
  -> backend/app/schemas/agent.py
  -> backend/app/schemas/auth.py
  -> backend/app/schemas/generated_post.py
  -> backend/app/services/firebase_service.py

backend/app/graphs/daily_marketing_graph.py
  -> backend/app/agents/product_selector.py
  -> backend/app/agents/content_strategy.py
  -> backend/app/agents/caption_agent.py
  -> backend/app/agents/prompt_agent.py
  -> backend/app/schemas/agent.py
  -> backend/app/schemas/auth.py
  -> backend/app/services/firebase_service.py
  -> backend/app/services/llm_service.py
  -> loads reference image memory for brand-grounded generation

backend/app/services/llm_service.py
  -> backend/app/config.py
  -> backend/app/schemas/business.py
  -> backend/app/schemas/generated_post.py
  -> backend/app/schemas/product.py
  -> backend/app/schemas/reference_image.py
  -> backend/app/schemas/scheduled_post.py
  -> Gemini Interactions API

backend/app/services/image_service.py
  -> backend/app/config.py
  -> backend/app/schemas/business.py
  -> backend/app/schemas/generated_post.py
  -> backend/app/schemas/product.py
  -> backend/app/schemas/reference_image.py
  -> backend/app/services/storage_service.py
  -> Hugging Face Inference Providers through huggingface_hub
  -> Pillow for image object serialization, controlled poster layout rendering, brand logo overlay, and product image composition
  -> Gemini Interactions API

backend/app/dependencies.py
  -> backend/app/services/firebase_service.py
  -> backend/app/schemas/auth.py

backend/app/services/firebase_service.py
  -> backend/app/config.py
  -> backend/app/schemas/auth.py
  -> backend/app/schemas/business.py
  -> backend/app/schemas/generated_post.py
  -> backend/app/schemas/generated_poster.py
  -> backend/app/schemas/product.py
  -> backend/app/schemas/reference_image.py
  -> backend/app/schemas/scheduled_post.py
  -> backend/app/services/image_service.py
  -> Firebase Admin SDK

backend/app/services/social_service.py
  -> backend/app/schemas/scheduled_post.py
  -> backend/app/schemas/generated_poster.py
  -> backend/app/config.py
  -> Meta Graph API adapter with mock fallback

backend/app/services/storage_service.py
  -> backend/app/config.py
  -> Firebase Admin Storage SDK
```

## Current Frontend Dependency Graph

```text
frontend/src/main.tsx
  -> frontend/src/app/App.tsx
  -> frontend/src/app/theme.ts
  -> frontend/src/auth/AuthContext.tsx
  -> frontend/src/lib/firebase.ts
  -> frontend/src/styles.css

frontend/src/app/App.tsx
  -> frontend/src/auth/AuthContext.tsx
  -> frontend/src/pages/ContentCalendar/ContentCalendarPage.tsx
  -> frontend/src/pages/Dashboard/DashboardPage.tsx
  -> frontend/src/pages/BusinessProfile/BusinessProfilePage.tsx
  -> frontend/src/pages/GeneratedContent/GeneratedContentPage.tsx
  -> frontend/src/pages/Login/LoginPage.tsx
  -> frontend/src/pages/Products/ProductsPage.tsx
  -> frontend/src/pages/ReferenceImages/ReferenceImagesPage.tsx

frontend/src/pages/Dashboard/DashboardPage.tsx
  -> frontend/src/auth/AuthContext.tsx
  -> frontend/src/services/api.ts

frontend/src/pages/GeneratedContent/GeneratedContentPage.tsx
  -> frontend/src/auth/AuthContext.tsx
  -> frontend/src/services/api.ts

frontend/src/pages/ContentCalendar/ContentCalendarPage.tsx
  -> frontend/src/auth/AuthContext.tsx
  -> frontend/src/services/api.ts

frontend/src/pages/BusinessProfile/BusinessProfilePage.tsx
  -> frontend/src/auth/AuthContext.tsx
  -> frontend/src/services/api.ts

frontend/src/pages/Products/ProductsPage.tsx
  -> frontend/src/auth/AuthContext.tsx
  -> frontend/src/services/api.ts

frontend/src/pages/ReferenceImages/ReferenceImagesPage.tsx
  -> frontend/src/auth/AuthContext.tsx
  -> frontend/src/services/api.ts

frontend/src/pages/Login/LoginPage.tsx
  -> frontend/src/auth/AuthContext.tsx

frontend/src/lib/firebase.ts
  -> Firebase Web SDK
```

## Planned Frontend Dependency Graph

```text
frontend/src/app
  -> frontend/src/pages
  -> frontend/src/components
  -> frontend/src/hooks
  -> frontend/src/services
  -> frontend/src/types
  -> frontend/src/lib
```

Planned rules:

- Pages compose components and call hooks/services.
- Components should avoid direct API calls unless they are feature-specific containers.
- Services own HTTP calls. Firebase client initialization lives in `frontend/src/lib/firebase.ts`.
- Hooks own frontend orchestration and state.
- Types define shared frontend contracts.
- `lib` stores reusable helpers.

## Planned Backend Dependency Graph

```text
backend/app/main.py
  -> backend/app/api
      -> backend/app/schemas
      -> backend/app/services
      -> backend/app/repositories
      -> backend/app/graphs

backend/app/graphs
  -> backend/app/agents
  -> backend/app/services
  -> backend/app/repositories

backend/app/agents
  -> backend/app/services/llm_service.py
  -> backend/app/schemas

backend/app/services
  -> external providers
  -> backend/app/config.py

backend/app/repositories
  -> backend/app/services/firebase_service.py
  -> backend/app/models
```

## Planned Critical Files

These files should be changed carefully once created:

- `backend/app/main.py`: application startup and route registration. Created in Phase 1.
- `backend/app/config.py`: environment settings and service configuration. Created in Phase 1.
- `backend/app/graphs/daily_marketing_graph.py`: core MVP agent workflow placeholder. Created in Phase 1.
- `backend/app/services/firebase_service.py`: database/storage integration.
- `backend/app/services/llm_service.py`: model provider abstraction.
- `backend/app/services/social_service.py`: Meta Graph API publishing adapter with mock fallback.
- `frontend/src/app/`: frontend shell and theme. Created in Phase 1.
- `frontend/src/lib/firebase.ts`: Firebase Web SDK initialization. Created after Firebase project config was supplied.
- `frontend/src/services/api.ts`: frontend/backend API contract. Created in Phase 1.

## Planned High-Impact Areas

### Agent Workflow

Changes can affect content quality, costs, latency, and logs.

### Firestore Schema

Changes can affect all API routes, frontend views, and analytics.

### Authentication Middleware

Changes can affect data isolation and security.

### Social Publishing

Changes can affect real public posts. Require explicit approval state.

### Prompt and Claim Generation

Changes can affect brand safety and health claim accuracy.

## Dependency Rules

- Agents should not directly write to Firestore unless the graph or service layer owns that responsibility.
- API routes should not contain long prompt logic.
- Frontend should not call third-party LLM or image APIs directly.
- Business-specific data access must include `businessId`.
- Social publishing must only use approved generated content.
- Agent logs should be written for every major workflow step.

## Unknowns

- Actual package manager.
- Actual frontend state management.
- Actual backend repository pattern.
- Actual test framework.

## Verification Notes

- Backend runtime import passed in the local virtualenv with bytecode writing disabled.
- Backend runtime import was not completed in the global Python environment because installed FastAPI and Starlette versions are incompatible.
- `backend/requirements.txt` pins Starlette for a clean virtualenv and includes `huggingface-hub`, `pillow`, and `python-multipart` for FLUX image generation, logo overlay, and upload handling.
- Node/npm were not available on PATH during this setup session, so frontend install/build was not run.

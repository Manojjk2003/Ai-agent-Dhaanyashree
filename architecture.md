# Architecture

## Documentation Maintenance Rule

Update this file whenever system boundaries, services, agents, deployment shape, third-party integrations, or major data flows change. Also update `memory.md` when the change affects project understanding.

## Current State

Phase 15 foundation scaffold exists. The frontend initializes Firebase, supports email/password sign in/sign up, gates the app by auth state, includes one business profile with brand kit uploads, product management with multiple uploaded product images, labelled reference image memory with uploads, daily plan generation, generated content review, manual content calendar, AI schedule time recommendation, poster generation/preview, template-based poster layout generation, and publish controls. The backend has health, current-user, asset upload, business profile, product, reference image, generated content, schedule, poster, social publishing, and daily-plan routes. Firebase Admin verification, Firebase Storage uploads, and Firestore business/product/reference-image/generated-content/scheduled-content/generated-poster persistence are implemented. Daily plan generation and schedule recommendation try Gemini when configured and fall back to deterministic generation when Gemini is unavailable. Content and poster prompts now use brand kit, business contact details, product images, product notes, and reference image labels/notes as active visual memory. Poster generation defaults to a controlled layout renderer. Social publishing defaults to mock and can publish through Meta Graph API when `SOCIAL_PROVIDER=meta` plus Meta credentials are configured.

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
  |       +--> Asset Upload API: implemented
  |       +--> Business/Profile APIs: implemented
  |       +--> Product APIs: implemented
  |       +--> Reference Image APIs: implemented
  |       +--> Generated Content APIs: implemented
  |       +--> Schedule APIs: implemented
  |       +--> Poster APIs: implemented
  |       +--> Social APIs: Meta publishing foundation with mock fallback
  |       +--> Daily Plan API: implemented
  |       +--> Analytics APIs: planned
  |       `--> Agent Log APIs: planned
  |
  +--> LangGraph Workflows
  |       +--> Daily Marketing Graph: Gemini-backed implementation with brand/product visual memory and fallback
  |       +--> SEO Graph
  |       +--> Analytics Recommendation Graph
  |       `--> Future Video Graph
  |
  +--> Services
  |       +--> LLM Service: Gemini Interactions API integration
  |       +--> Image Service: Hugging Face FLUX, Gemini image generation, logo overlay, plus fallback SVG
  |       +--> Storage Service: Firebase Storage uploads
  |       +--> Firebase Service: Firestore/Auth integration
  |       +--> Social Service: Meta Graph API adapter with mock fallback
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

Current daily plan behavior:

```text
Frontend dashboard
  |
  +--> Sends Firebase ID token
  |
  v
POST /agent/run-daily-plan
  |
  v
Backend verifies Firebase token
  |
  v
Backend loads one business profile, products, and labelled reference images
  |
  v
Product selection agent chooses product
  |
  v
LLM service tries Gemini with business, brand kit, product memory, and reference visual memory
  |
  +--> If Gemini succeeds, use LLM caption, hashtags, and poster prompt
  |
  `--> If Gemini fails, run deterministic content strategy, caption, hashtag, and prompt agents
  |
  v
Backend returns selected product, idea, caption, hashtags, and poster prompt
  |
  v
Generated post is saved in the top-level generated_posts collection with business_id
  |
  v
Content review screen can edit and approve or reject it
```

Current calendar behavior:

```text
Content review screen
  |
  v
User approves generated content
  |
  v
Calendar screen lists approved generated posts
  |
  v
User can request AI recommended posting time
  |
  v
Gemini/fallback recommends time, reason, confidence, and alternatives
  |
  v
User accepts or edits date/time and schedules post
  |
  v
Backend writes scheduled_posts document and marks generated post as scheduled
  |
  v
Calendar screen shows manual scheduled queue
```

Current poster behavior:

```text
Content review screen
  |
  v
User clicks Generate Poster
  |
  v
Backend loads generated post, business profile, selected product, and reference images
  |
  v
Image service receives visual context and template
  |
  +--> Layout renderer creates controlled branded PNG when business visual context exists
  |
  +--> Older image provider path can use Hugging Face FLUX/Gemini/fallback when layout context is unavailable
  |
  `--> If provider fails, save fallback SVG poster with error_message
  |
  v
Backend writes generated_posters metadata
  |
  v
Frontend previews poster from Firebase Storage URL, or /static/posters only if Storage upload fails locally
```

Current asset upload behavior:

```text
Business, Products, or References screen
  |
  v
User selects local image file
  |
  v
POST /assets/upload multipart request with Firebase ID token
  |
  v
Backend stores file in Firebase Storage
  |
  v
Backend returns download URL and storage path
  |
  v
Frontend saves URL into brand kit, product gallery, or reference image record
```

Current social publish behavior:

```text
Calendar screen
  |
  v
User clicks Publish Now on a scheduled post
  |
  v
POST /social/publish-now
  |
  v
Backend loads scheduled_posts document and latest generated poster
  |
  v
Social service publishes through Meta Graph API when configured, otherwise records mock response
  |
  v
Backend marks scheduled post and source generated post as published
  |
  v
Calendar shows published timestamp, provider, and platform post id
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
- Keep local poster file fallback only as a development safety net when Firebase Storage is unavailable.

## Unknowns

- Final LLM provider.
- Final image generation provider.
- Final hosting provider.
- Social platform permission status.
- Whether agency-style multi-business support is needed after the one-business MVP.

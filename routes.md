# Routes

## Documentation Maintenance Rule

Update this file whenever frontend pages, layouts, protected routes, backend routes, or route permissions change. If a route exposes or changes an API contract, update `api-map.md` too.

## Current State

Phase 12 scaffold routes exist. Frontend has an in-app auth-gated dashboard/business/products/references/content/calendar view switch without React Router. Backend has health, auth, asset upload, business profile, product, reference image, generated content, schedule, poster, mock social publishing, and daily-plan endpoints.

## Planned Frontend Routes

| Route | File | Purpose | Auth Required |
|---|---|---|---|
| Login view | `frontend/src/pages/Login/LoginPage.tsx` | Email/password sign in and sign up | No |
| Dashboard view | `frontend/src/pages/Dashboard/DashboardPage.tsx` | Main dashboard shell | Yes |
| Business view | `frontend/src/pages/BusinessProfile/BusinessProfilePage.tsx` | Business profile, audience, goals, brand tone | Yes |
| Products view | `frontend/src/pages/Products/ProductsPage.tsx` | Product memory management | Yes |
| References view | `frontend/src/pages/ReferenceImages/ReferenceImagesPage.tsx` | Labelled visual reference images | Yes |
| Content view | `frontend/src/pages/GeneratedContent/GeneratedContentPage.tsx` | Review generated captions, hashtags, and poster prompts | Yes |
| Calendar view | `frontend/src/pages/ContentCalendar/ContentCalendarPage.tsx` | Schedule approved generated content | Yes |
| `/login` | `frontend/src/pages/Login/` | Future React Router login route | No |
| `/` | `frontend/src/pages/Dashboard/` | Future React Router dashboard route | Yes |
| `/business` | `frontend/src/pages/BusinessProfile/` | Future React Router business profile route | Yes |
| `/products` | `frontend/src/pages/Products/` | Future React Router product route | Yes |
| `/calendar` | `frontend/src/pages/ContentCalendar/` | Content calendar and scheduling | Yes |
| `/content` | `frontend/src/pages/GeneratedContent/` | Future React Router generated content route | Yes |
| `/posters` | `frontend/src/pages/Posters/` | Generated poster gallery and editor/review screen | Yes |
| `/seo` | `frontend/src/pages/SEO/` | Keywords, blog topics, FAQs, metadata | Yes |
| `/social` | `frontend/src/pages/SocialMedia/` | Social accounts, publishing, scheduling | Yes |
| `/analytics` | `frontend/src/pages/Analytics/` | Content and sales performance | Yes |
| `/recommendations` | `frontend/src/pages/Recommendations/` | Suggested next actions | Yes |
| `/agent-logs` | `frontend/src/pages/AgentLogs/` | Agent run history and decision logs | Yes |
| `/settings` | `frontend/src/pages/Settings/` | Account, integrations, API settings | Yes |

## Planned Backend Routes

| Method | Route | Purpose | Auth Required |
|---|---|---|---|
| `GET` | `/health` | Backend health check, implemented | No |
| `GET` | `/me` | Current Firebase user context, implemented | Yes |
| `POST` | `/assets/upload` | Upload brand/reference/product/generated poster images to Firebase Storage, implemented | Yes |
| `POST` | `/business/profile` | Create or update business profile, implemented | Yes |
| `GET` | `/business/profile` | Read current business profile, implemented | Yes |
| `POST` | `/products` | Create product, implemented | Yes |
| `GET` | `/products` | List products, implemented | Yes |
| `GET` | `/products/{product_id}` | Read product, implemented | Yes |
| `PATCH` | `/products/{product_id}` | Update product, implemented | Yes |
| `DELETE` | `/products/{product_id}` | Delete product, implemented | Yes |
| `POST` | `/reference-images` | Create labelled visual reference, implemented | Yes |
| `GET` | `/reference-images` | List labelled visual references, implemented | Yes |
| `PATCH` | `/reference-images/{reference_image_id}` | Update labelled visual reference, implemented | Yes |
| `DELETE` | `/reference-images/{reference_image_id}` | Delete labelled visual reference, implemented | Yes |
| `POST` | `/agent/run-daily-plan` | Generate daily marketing plan from one business profile and products, implemented | Yes |
| `GET` | `/content/plans` | List content plans | Yes |
| `GET` | `/content/posts` | List generated posts, implemented | Yes |
| `GET` | `/content/posts/{post_id}` | Read generated post, implemented | Yes |
| `PATCH` | `/content/posts/{post_id}` | Edit generated post and review status, implemented | Yes |
| `DELETE` | `/content/posts/{post_id}` | Reject and delete generated post, implemented | Yes |
| `GET` | `/schedule/posts` | List scheduled posts, implemented | Yes |
| `POST` | `/schedule/posts` | Schedule approved generated content, implemented | Yes |
| `POST` | `/schedule/recommend-time` | Recommend best posting time, implemented | Yes |
| `DELETE` | `/schedule/posts/{scheduled_post_id}` | Cancel scheduled post, implemented | Yes |
| `GET` | `/posters` | List generated posters, implemented | Yes |
| `POST` | `/posters/generate` | Generate poster for generated content, implemented | Yes |
| `POST` | `/social/schedule` | Real social platform scheduling, future | Yes |
| `POST` | `/social/publish-now` | Mock publish scheduled content immediately, implemented | Yes |
| `GET` | `/analytics` | Fetch analytics summary | Yes |
| `GET` | `/recommendations` | Fetch recommendations | Yes |
| `GET` | `/agent/logs` | List agent logs | Yes |
| `GET` | `/agent/logs/{run_id}` | Read one agent run | Yes |

## Auth and Protection Notes

- Frontend protected routes should require Firebase Auth state.
- Backend protected routes should require `Authorization: Bearer <firebase_id_token>`.
- Backend should resolve `userId` and `businessId` before reading or writing data.

## Unknowns

- Exact frontend router library setup.
- Whether business selection route is needed for multi-business users.
- Final API versioning scheme, for example `/api/v1`.

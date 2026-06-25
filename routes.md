# Routes

## Documentation Maintenance Rule

Update this file whenever frontend pages, layouts, protected routes, backend routes, or route permissions change. If a route exposes or changes an API contract, update `api-map.md` too.

## Current State

Phase 1 scaffold routes exist. Frontend has a single dashboard shell without React Router. Backend has health and daily-plan endpoints.

## Planned Frontend Routes

| Route | File | Purpose | Auth Required |
|---|---|---|---|
| `/` | `frontend/src/pages/Dashboard/DashboardPage.tsx` | Current dashboard shell | No |
| `/login` | `frontend/src/pages/Login/` | User sign in | No |
| `/` | `frontend/src/pages/Dashboard/` | Main protected business dashboard after auth is added | Yes |
| `/business` | `frontend/src/pages/BusinessProfile/` | Business profile, audience, goals, brand tone | Yes |
| `/products` | `frontend/src/pages/Products/` | Product management | Yes |
| `/calendar` | `frontend/src/pages/ContentCalendar/` | Content calendar and scheduling | Yes |
| `/content` | `frontend/src/pages/GeneratedContent/` | Generated captions, hashtags, and post drafts | Yes |
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
| `GET` | `/me` | Current user context | Yes |
| `POST` | `/business/profile` | Create or update business profile | Yes |
| `GET` | `/business/profile` | Read current business profile | Yes |
| `POST` | `/products` | Create product | Yes |
| `GET` | `/products` | List products | Yes |
| `GET` | `/products/{product_id}` | Read product | Yes |
| `PATCH` | `/products/{product_id}` | Update product | Yes |
| `DELETE` | `/products/{product_id}` | Delete or archive product | Yes |
| `POST` | `/agent/run-daily-plan` | Generate daily marketing plan and assets, scaffold implemented without auth | Planned Yes |
| `GET` | `/content/plans` | List content plans | Yes |
| `GET` | `/content/posts` | List generated posts | Yes |
| `PATCH` | `/content/posts/{post_id}` | Edit generated post | Yes |
| `POST` | `/poster/generate` | Generate poster for post or prompt | Yes |
| `POST` | `/social/schedule` | Schedule approved post | Yes |
| `POST` | `/social/publish-now` | Publish approved post immediately | Yes |
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

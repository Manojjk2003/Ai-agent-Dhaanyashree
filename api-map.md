# API Map

## Documentation Maintenance Rule

Update this file whenever an endpoint is added, removed, renamed, or its request/response shape changes. If the endpoint touches database collections, update `database-map.md`. If it is exposed by a route, update `routes.md`.

## Current State

Phase 1 backend scaffold exists. `GET /health` and `POST /agent/run-daily-plan` are implemented. The daily-plan endpoint currently returns placeholder IDs from a placeholder graph rather than running real agents.

## API Inventory

| Method | Route | Purpose | Used By |
|---|---|---|---|
| `GET` | `/health` | Health check, implemented | Hosting, uptime checks, frontend dashboard |
| `GET` | `/me` | Return authenticated user and business context | Frontend shell |
| `POST` | `/business/profile` | Create or update business profile | Business Profile page |
| `GET` | `/business/profile` | Read business profile | Dashboard, agents |
| `POST` | `/products` | Create product | Products page |
| `GET` | `/products` | List products | Dashboard, Products page, agents |
| `GET` | `/products/{product_id}` | Read product details | Products page |
| `PATCH` | `/products/{product_id}` | Update product | Products page |
| `DELETE` | `/products/{product_id}` | Archive/delete product | Products page |
| `POST` | `/agent/run-daily-plan` | Generate placeholder daily marketing plan, implemented scaffold | Dashboard, future scheduler |
| `GET` | `/content/plans` | List content plans | Calendar |
| `GET` | `/content/posts` | List generated posts | Generated Content page |
| `PATCH` | `/content/posts/{post_id}` | Edit generated post | Generated Content page |
| `POST` | `/poster/generate` | Generate poster | Posters page, daily workflow |
| `POST` | `/social/schedule` | Schedule approved content | Calendar, Social page |
| `POST` | `/social/publish-now` | Publish approved content | Social page |
| `GET` | `/analytics` | Read performance summary | Dashboard, Analytics page |
| `GET` | `/recommendations` | Read recommended actions | Dashboard |
| `GET` | `/agent/logs` | List agent logs | Agent Logs page |
| `GET` | `/agent/logs/{run_id}` | Read detailed agent run | Agent Logs page |

## Planned Contract Sketches

### `POST /business/profile`

Purpose: save business memory.

Request:

```json
{
  "businessName": "Example Millet Foods",
  "industry": "Health food",
  "targetAudience": ["working mothers", "health-conscious families"],
  "brandTone": "warm, trustworthy, practical",
  "goals": ["increase daily orders", "grow Instagram reach"]
}
```

Response:

```json
{
  "businessId": "business_123",
  "updated": true
}
```

### `POST /products`

Purpose: create a product for marketing memory.

Request:

```json
{
  "name": "Ragi Malt",
  "benefits": ["High calcium", "Rich fiber", "Healthy breakfast"],
  "price": 199,
  "category": "Breakfast",
  "targetAudience": ["kids", "families"]
}
```

Response:

```json
{
  "productId": "product_123"
}
```

### `POST /agent/run-daily-plan`

Purpose: run the MVP marketing workflow.

Current request:

```json
{
  "business_id": "business_123",
  "run_date": "2026-06-25",
  "platforms": ["instagram", "facebook"],
  "require_poster": true
}
```

Current response:

```json
{
  "run_id": "run_123",
  "content_plan_id": "plan_123",
  "post_id": "post_123",
  "poster_id": "poster_123",
  "status": "ready_for_review",
  "summary": "Daily marketing graph scaffold completed..."
}
```

Implementation note: the Python schema uses snake_case fields. A future frontend convention decision should decide whether to keep snake_case over the wire or add aliases for camelCase.

### `PATCH /content/posts/{post_id}`

Purpose: edit generated content before approval.

Request:

```json
{
  "caption": "Updated caption",
  "hashtags": ["#millets", "#healthybreakfast"],
  "status": "approved"
}
```

Response:

```json
{
  "postId": "post_123",
  "updated": true
}
```

### `POST /social/schedule`

Purpose: schedule approved content.

Request:

```json
{
  "postId": "post_123",
  "platforms": ["instagram"],
  "scheduledAt": "2026-06-25T09:30:00+05:30"
}
```

Response:

```json
{
  "scheduledPostId": "scheduled_123",
  "status": "scheduled"
}
```

## Error Handling Standard

Planned API error shape:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Product name is required",
    "details": {}
  }
}
```

## Unknowns

- Final route prefix.
- Exact validation library.
- Exact auth dependency implementation.
- Pagination and filtering parameters.

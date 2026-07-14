# API Map

## Documentation Maintenance Rule

Update this file whenever an endpoint is added, removed, renamed, or its request/response shape changes. If the endpoint touches database collections, update `database-map.md`. If it is exposed by a route, update `routes.md`.

## Current State

Phase 4 backend scaffold exists. `GET /health`, `GET /me`, business profile APIs, product APIs, and `POST /agent/run-daily-plan` are implemented. Protected endpoints require a Firebase ID token. The daily-plan endpoint reads the authenticated user's one business profile and products, then returns a deterministic generated marketing plan.

## API Inventory

| Method | Route | Purpose | Used By |
|---|---|---|---|
| `GET` | `/health` | Health check, implemented | Hosting, uptime checks, frontend dashboard |
| `GET` | `/me` | Return authenticated Firebase user | Frontend shell |
| `POST` | `/business/profile` | Create or update business profile, implemented | Business Profile page |
| `GET` | `/business/profile` | Read business profile, implemented | Business Profile page, future agents |
| `POST` | `/products` | Create product, implemented | Products page |
| `GET` | `/products` | List products, implemented | Dashboard, Products page, future agents |
| `GET` | `/products/{product_id}` | Read product details, implemented | Products page |
| `PATCH` | `/products/{product_id}` | Update product, implemented | Products page |
| `DELETE` | `/products/{product_id}` | Delete product, implemented | Products page |
| `POST` | `/agent/run-daily-plan` | Generate daily marketing plan from business profile and products | Dashboard, future scheduler |
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

Protected requests use:

```text
Authorization: Bearer <firebase_id_token>
```

Swagger UI is available at:

```text
http://localhost:8000/docs
```

Use the Authorize button and paste only the Firebase ID token value, not the `Bearer` prefix.

### `GET /me`

Response:

```json
{
  "uid": "firebase_uid",
  "email": "owner@example.com",
  "name": "Business Owner"
}
```

### `POST /business/profile`

Purpose: save business memory.

Request:

```json
{
  "business_name": "Example Millet Foods",
  "industry": "Health food",
  "description": "Millet-based healthy breakfast products",
  "target_audience": ["working mothers", "health-conscious families"],
  "brand_tone": "warm, trustworthy, practical",
  "goals": ["increase daily orders", "grow Instagram reach"]
}
```

Response:

```json
{
  "business_id": "firebase_uid",
  "owner_user_id": "firebase_uid",
  "business_name": "Example Millet Foods",
  "industry": "Health food",
  "description": "Millet-based healthy breakfast products",
  "target_audience": ["working mothers", "health-conscious families"],
  "brand_tone": "warm, trustworthy, practical",
  "goals": ["increase daily orders", "grow Instagram reach"],
  "updated": true
}
```

### `GET /business/profile`

Response:

```json
{
  "business_id": "firebase_uid",
  "owner_user_id": "firebase_uid",
  "business_name": "Example Millet Foods",
  "industry": "Health food",
  "description": "Millet-based healthy breakfast products",
  "target_audience": ["working mothers", "health-conscious families"],
  "brand_tone": "warm, trustworthy, practical",
  "goals": ["increase daily orders"],
  "updated": false
}
```

### `POST /products`

Purpose: create a product for marketing memory.

Request:

```json
{
  "name": "Ragi Malt",
  "category": "Breakfast",
  "description": "Instant ragi breakfast drink",
  "benefits": ["High calcium", "Rich fiber", "Healthy breakfast"],
  "ingredients": ["Ragi", "Jaggery"],
  "price": 199,
  "target_audience": ["kids", "families"],
  "image_url": "",
  "is_active": true
}
```

Response:

```json
{
  "product_id": "product_123",
  "business_id": "firebase_uid",
  "name": "Ragi Malt",
  "category": "Breakfast",
  "description": "Instant ragi breakfast drink",
  "benefits": ["High calcium", "Rich fiber", "Healthy breakfast"],
  "ingredients": ["Ragi", "Jaggery"],
  "price": 199,
  "target_audience": ["kids", "families"],
  "image_url": "",
  "is_active": true
}
```

### `GET /products`

Response:

```json
[
  {
    "product_id": "product_123",
    "business_id": "firebase_uid",
    "name": "Ragi Malt",
    "category": "Breakfast",
    "description": "Instant ragi breakfast drink",
    "benefits": ["High calcium"],
    "ingredients": ["Ragi"],
    "price": 199,
    "target_audience": ["families"],
    "image_url": "",
    "is_active": true
  }
]
```

### `POST /agent/run-daily-plan`

Purpose: run the MVP marketing workflow.

Current request:

```json
{
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
  "summary": "Generated an educational post for Ragi Malt using Dhaanyashree's business profile and product memory.",
  "business_name": "Dhaanyashree",
  "selected_product_id": "product_123",
  "selected_product_name": "Ragi Malt",
  "selection_reason": "Ragi Malt has the strongest product memory available right now; benefits: High calcium, Rich fiber",
  "content_type": "Educational post",
  "content_idea": "Show how Ragi Malt helps with high calcium in everyday life.",
  "caption": "Make today's routine healthier with Ragi Malt...",
  "hashtags": ["#RagiMalt", "#Breakfast", "#HealthyChoices"],
  "poster_prompt": "Commercial social media poster for Dhaanyashree..."
}
```

Implementation note: the Python schema uses snake_case fields.

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

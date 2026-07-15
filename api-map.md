# API Map

## Documentation Maintenance Rule

Update this file whenever an endpoint is added, removed, renamed, or its request/response shape changes. If the endpoint touches database collections, update `database-map.md`. If it is exposed by a route, update `routes.md`.

## Current State

Phase 14 backend scaffold exists. `GET /health`, `GET /me`, protected asset upload, business profile APIs with brand kit fields, product APIs with image galleries, reference image APIs, generated content APIs, schedule APIs, poster APIs, mock social publish API, and `POST /agent/run-daily-plan` are implemented. Protected endpoints require a Firebase ID token. Brand, reference, product, and generated poster images are stored in Firebase Storage when configured. Brand kit, uploaded product images, and labelled reference image memory are active generation context. Poster generation supports template-based branded layouts and stores the final raster poster when configured.

## API Inventory

| Method | Route | Purpose | Used By |
|---|---|---|---|
| `GET` | `/health` | Health check, implemented | Hosting, uptime checks, frontend dashboard |
| `GET` | `/me` | Return authenticated Firebase user | Frontend shell |
| `POST` | `/assets/upload` | Upload brand/reference/product/generated poster images to Firebase Storage | Business, Products, References, Poster service |
| `POST` | `/business/profile` | Create or update business profile, implemented | Business Profile page |
| `GET` | `/business/profile` | Read business profile, implemented | Business Profile page, future agents |
| `POST` | `/products` | Create product, implemented | Products page |
| `GET` | `/products` | List products, implemented | Dashboard, Products page, future agents |
| `GET` | `/products/{product_id}` | Read product details, implemented | Products page |
| `PATCH` | `/products/{product_id}` | Update product, implemented | Products page |
| `DELETE` | `/products/{product_id}` | Delete product, implemented | Products page |
| `POST` | `/reference-images` | Create labelled visual reference | Reference Images page |
| `GET` | `/reference-images` | List labelled visual references | Reference Images page, future image agent |
| `PATCH` | `/reference-images/{reference_image_id}` | Update visual reference | Reference Images page |
| `DELETE` | `/reference-images/{reference_image_id}` | Delete visual reference | Reference Images page |
| `POST` | `/agent/run-daily-plan` | Generate daily marketing plan and save generated post | Dashboard, Content page |
| `GET` | `/content/plans` | List content plans | Calendar |
| `GET` | `/content/posts` | List generated posts, implemented | Generated Content page |
| `GET` | `/content/posts/{post_id}` | Read generated post, implemented | Generated Content page |
| `PATCH` | `/content/posts/{post_id}` | Edit caption, hashtags, poster prompt, and review status | Generated Content page |
| `DELETE` | `/content/posts/{post_id}` | Reject and delete generated post | Generated Content page |
| `GET` | `/schedule/posts` | List manually scheduled posts | Calendar page |
| `POST` | `/schedule/posts` | Schedule approved generated content | Calendar page |
| `POST` | `/schedule/recommend-time` | Recommend best time for approved generated content | Calendar page |
| `DELETE` | `/schedule/posts/{scheduled_post_id}` | Cancel scheduled post and return source post to approved | Calendar page |
| `GET` | `/posters` | List generated posters | Content Review |
| `POST` | `/posters/generate` | Generate poster for generated content | Content Review |
| `POST` | `/social/schedule` | Publish/schedule through real social platform API, future | Social page |
| `POST` | `/social/publish-now` | Publish scheduled content through Meta when configured, otherwise mock, and mark it published | Calendar page |
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

### `POST /assets/upload`

Purpose: upload image files through the backend to Firebase Storage.

Request: multipart form data.

Fields:

- `asset_type`: `brand_logo`, `brand_avatar`, `reference_image`, `product_image`, or `generated_poster`
- `owner_id`: optional product/reference/post identifier
- `file`: image file

Response:

```json
{
  "image_url": "https://firebasestorage.googleapis.com/...",
  "storage_path": "businesses/firebase_uid/product-images/product_123/file.png",
  "content_type": "image/png",
  "file_name": "file.png"
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
  "website_url": "https://example.com",
  "address": "Shop address",
  "phone_number": "+91...",
  "email": "owner@example.com",
  "license_number": "FSSAI...",
  "target_audience": ["working mothers", "health-conscious families"],
  "brand_tone": "warm, trustworthy, practical",
  "goals": ["increase daily orders", "grow Instagram reach"],
  "brand_kit": {
    "logo_url": "https://example.com/logo.png",
    "avatar_url": "https://example.com/avatar.png",
    "primary_color": "#1b7b68",
    "secondary_color": "#d9542b",
    "accent_color": "#f2c94c",
    "font_family": "Inter",
    "heading_font_family": "Poppins",
    "visual_style": ["Clean", "Natural light"],
    "brand_keywords": ["healthy", "traditional"]
  }
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
  "image_urls": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
  "image_notes": "Use front pack and serving bowl angle for posters.",
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
    "image_urls": [],
    "image_notes": "",
    "is_active": true
  }
]
```

### `POST /reference-images`

Purpose: create labelled visual memory for things the AI may not know, such as foxtail millet, packaging, ingredient closeups, or preferred style examples.

Request:

```json
{
  "name": "Foxtail Millet",
  "image_url": "https://example.com/foxtail-millet.jpg",
  "reference_type": "ingredient",
  "labels": ["foxtail millet", "raw grain", "yellow millet"],
  "notes": "Use this when the product or prompt mentions foxtail millet."
}
```

Response:

```json
{
  "reference_image_id": "ref_123",
  "business_id": "firebase_uid",
  "name": "Foxtail Millet",
  "image_url": "https://example.com/foxtail-millet.jpg",
  "reference_type": "ingredient",
  "labels": ["foxtail millet", "raw grain", "yellow millet"],
  "notes": "Use this when the product or prompt mentions foxtail millet.",
  "created_at": "2026-07-14T10:00:00+00:00",
  "updated_at": "2026-07-14T10:00:00+00:00"
}
```

### `GET /reference-images`

Response: list of the same objects returned by `POST /reference-images`.

### `POST /agent/run-daily-plan`

Purpose: run the MVP marketing workflow and save the result as generated content.

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
  "poster_prompt": "Commercial social media poster for Dhaanyashree...",
  "generation_source": "gemini"
}
```

Implementation note: the Python schema uses snake_case fields.

### `GET /content/posts`

Response:

```json
[
  {
    "post_id": "post_123",
    "business_id": "firebase_uid",
    "run_id": "run_123",
    "content_plan_id": "plan_123",
    "product_id": "product_123",
    "product_name": "Ragi Malt",
    "selection_reason": "Strongest product memory",
    "content_type": "Educational post",
    "content_idea": "Show how Ragi Malt helps with high calcium.",
    "caption": "Make today's routine healthier...",
    "hashtags": ["#RagiMalt"],
    "poster_prompt": "Commercial social media poster...",
    "platforms": ["instagram"],
    "run_date": "2026-07-14",
    "status": "ready_for_review",
    "generation_source": "gemini",
    "scheduled_post_id": null,
    "scheduled_at": null,
    "created_at": "2026-07-14T10:00:00+00:00",
    "updated_at": "2026-07-14T10:00:00+00:00"
  }
]
```

`generation_source` is `gemini` when the configured Gemini provider produced the content and `fallback` when the rule-based local generator produced it.

### `PATCH /content/posts/{post_id}`

Purpose: edit generated content before approval.

Request:

```json
{
  "caption": "Updated caption",
  "hashtags": ["#millets", "#healthybreakfast"],
  "poster_prompt": "Updated poster prompt",
  "status": "approved"
}
```

Response:

```json
{
  "post_id": "post_123",
  "status": "approved"
}
```

### `DELETE /content/posts/{post_id}`

Purpose: reject a generated draft and remove it from Firestore.

Response:

```text
204 No Content
```

### `GET /schedule/posts`

Purpose: list scheduled posts in the manual calendar queue.

Response:

```json
[
  {
    "scheduled_post_id": "scheduled_123",
    "business_id": "firebase_uid",
    "post_id": "post_123",
    "product_id": "product_123",
    "product_name": "Ragi Malt",
    "content_type": "Product Spotlight",
    "caption": "Start your day with...",
    "hashtags": ["#RagiMalt"],
    "poster_prompt": "Bright kitchen counter...",
    "platforms": ["instagram"],
    "scheduled_at": "2026-07-15T10:00:00+05:30",
    "published_at": null,
    "platform_post_id": null,
    "error_message": null,
    "status": "scheduled",
    "created_at": "2026-07-14T10:00:00+00:00",
    "updated_at": "2026-07-14T10:00:00+00:00"
  }
]
```

### `POST /schedule/posts`

Purpose: schedule approved content.

Request:

```json
{
  "post_id": "post_123",
  "platforms": ["instagram"],
  "scheduled_at": "2026-07-15T10:00:00+05:30"
}
```

Response: same object as `GET /schedule/posts`.

### `POST /schedule/recommend-time`

Purpose: recommend a posting time for approved generated content. Gemini is used when configured; otherwise the backend returns a heuristic fallback recommendation.

Request:

```json
{
  "post_id": "post_123",
  "target_date": "2026-07-15",
  "platforms": ["instagram"]
}
```

Response:

```json
{
  "recommended_at": "2026-07-15T08:30:00",
  "reason": "Morning is a strong fit for food and health content because people are planning meals and routines.",
  "confidence": 0.72,
  "alternative_slots": ["2026-07-15T12:30:00", "2026-07-15T18:30:00"],
  "generation_source": "gemini"
}
```

### `DELETE /schedule/posts/{scheduled_post_id}`

Purpose: cancel a scheduled post and return the source generated post to `approved`.

Response:

```text
204 No Content
```

### `POST /social/publish-now`

Purpose: publish a scheduled post now. The backend loads the latest generated poster for the source post. When `SOCIAL_PROVIDER=meta` and Meta credentials are configured, it publishes through Meta Graph API. Otherwise, it records a mock publish response. The schedule plus source generated post are marked as `published` on success.

Request:

```json
{
  "scheduled_post_id": "scheduled_123"
}
```

Response:

```json
{
  "scheduled_post": {
    "scheduled_post_id": "scheduled_123",
    "business_id": "firebase_uid",
    "post_id": "post_123",
    "product_id": "product_123",
    "product_name": "Ragi Malt",
    "content_type": "Product Spotlight",
    "caption": "Start your day with...",
    "hashtags": ["#RagiMalt"],
    "poster_prompt": "Bright kitchen counter...",
    "platforms": ["instagram"],
    "scheduled_at": "2026-07-15T10:00:00+05:30",
    "published_at": "2026-07-14T10:00:00+00:00",
    "platform_post_id": "mock_instagram_abc123",
    "error_message": null,
    "status": "published",
    "created_at": "2026-07-14T10:00:00+00:00",
    "updated_at": "2026-07-14T10:00:00+00:00"
  },
  "provider": "meta",
  "platform_post_id": "instagram:1789...,facebook:1234...",
  "message": "Published through Meta Graph API."
}
```

### `GET /posters`

Purpose: list generated poster metadata.

Response:

```json
[
  {
    "poster_id": "poster_123",
    "business_id": "firebase_uid",
    "post_id": "post_123",
    "product_id": "product_123",
    "product_name": "Ragi Malt",
    "prompt": "Commercial social media poster...",
    "image_url": "http://localhost:8000/static/posters/poster_123.png",
    "storage_path": "generated/posters/poster_123.png",
    "mime_type": "image/png",
    "provider": "layout",
    "error_message": null,
    "status": "generated",
    "created_at": "2026-07-14T10:00:00+00:00",
    "updated_at": "2026-07-14T10:00:00+00:00"
  }
]
```

### `POST /posters/generate`

Purpose: generate a poster image from a generated post. The default path uses the controlled brand layout renderer when business visual context exists. Older provider paths support Hugging Face FLUX, Gemini image generation, and fallback SVG poster generation when layout context is unavailable.

Request:

```json
{
  "post_id": "post_123",
  "template": "auto"
}
```

`template` can be `auto`, `product_spotlight`, `educational`, `offer`, or `festival`.

Response: same object as `GET /posters`.

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

# Database Map

## Documentation Maintenance Rule

Update this file whenever Firestore collections, document fields, storage paths, indexes, relationships, or lifecycle rules change. If an API reads/writes the changed data, update `api-map.md` too.

## Current State

Business profile, product, and generated post read/write are implemented through the backend Firebase Admin service. The frontend Firebase web client is initialized for Auth, Firestore, Storage, and Analytics.

## Firestore Collections

### `users`

Purpose: map Firebase Auth users to application profile data.

Fields:

- `uid`
- `email`
- `displayName`
- `createdAt`
- `updatedAt`
- `defaultBusinessId`

Relationships:

- Current product decision: one signed-in user maps to one business document using `businesses/{firebase_uid}`.

### `businesses`

Purpose: top-level business entity.

Fields:

- `businessId`
- `ownerUserId`
- `business_name`
- `industry`
- `description`
- `goals`
- `target_audience`
- `brand_tone`
- `createdAt`
- `updatedAt`

Current implementation detail:

- Document path: `businesses/{firebase_uid}`
- Stored field names currently use snake_case, matching the API schemas.

Relationships:

- Parent for products, brand profiles, content plans, analytics, recommendations, and logs.
- Current MVP uses one business profile per user, not multiple businesses per user.

### `brand_profiles`

Purpose: store brand tone, audience, claims, visual preferences, and marketing constraints.

Fields:

- `businessId`
- `targetAudience`
- `brandTone`
- `visualStyle`
- `allowedClaims`
- `blockedClaims`
- `preferredLanguages`
- `updatedAt`

### `products`

Purpose: products the agent can promote.

Fields:

- `businessId`
- `name`
- `description`
- `benefits`
- `ingredients`
- `price`
- `category`
- `image_url`
- `targetAudience`
- `isActive`
- `createdAt`
- `updatedAt`

Current implementation detail:

- Document path: `products/{productId}`
- Each product stores `business_id` to link it to the user's one business profile.
- Stored field names currently use snake_case, matching the API schemas.
- `DELETE /products/{product_id}` physically deletes the product document in the current MVP.

### `trends`

Purpose: trend signals relevant to the business.

Fields:

- `businessId`
- `trend`
- `source`
- `score`
- `reason`
- `relatedProducts`
- `createdAt`

### `competitors`

Purpose: competitor profiles and observed content patterns.

Fields:

- `businessId`
- `name`
- `platform`
- `profileUrl`
- `contentPatterns`
- `hashtags`
- `engagementNotes`
- `updatedAt`

### `content_plans`

Purpose: 7-day, 30-day, or campaign-level content plan.

Fields:

- `businessId`
- `planType`
- `startDate`
- `endDate`
- `goals`
- `status`
- `createdByRunId`
- `createdAt`
- `updatedAt`

### `generated_posts`

Purpose: generated text content and approval state.

Fields:

- `businessId`
- `contentPlanId`
- `productId`
- `product_name`
- `selection_reason`
- `trendId`
- `contentType`
- `content_idea`
- `platforms`
- `caption`
- `cta`
- `hashtags`
- `poster_prompt`
- `status`
- `generation_source`
- `scheduledPostId`
- `createdByRunId`
- `createdAt`
- `updatedAt`

Current implementation detail:

- Document path: `generated_posts/{postId}`
- Each generated post stores `business_id` to link it to the user's one business profile.
- Generated daily plans are saved here automatically by `POST /agent/run-daily-plan`.
- Content review updates `caption`, `hashtags`, `poster_prompt`, and `status`.
- `generation_source` is `gemini` for Gemini-generated content and `fallback` for rule-generated content.
- Rejecting generated content deletes the `generated_posts/{postId}` document in the current MVP.

Statuses:

- `draft`
- `ready_for_review`
- `approved`
- `scheduled`
- `published`
- `rejected`

### `generated_posters`

Purpose: poster metadata and storage references.

Fields:

- `business_id`
- `post_id`
- `product_id`
- `product_name`
- `prompt`
- `storage_path`
- `image_url`
- `mime_type`
- `provider`
- `error_message`
- `status`
- `created_at`
- `updated_at`

Current implementation detail:

- Document path: `generated_posters/{posterId}`
- Each generated poster stores `business_id` to link it to the user's one business profile.
- Poster image files are saved locally under `generated/posters` and served by FastAPI at `/static/posters`.
- `provider` is `huggingface` when Hugging Face FLUX image generation succeeds, `gemini` when Gemini image generation succeeds, and `fallback` when the local SVG poster generator is used.
- `error_message` stores the image provider failure reason when the backend falls back to SVG.
- Later phase should move binary poster files to Firebase Storage and keep Firestore metadata stable.

### `generated_videos`

Purpose: future video/reel outputs.

Fields:

- `businessId`
- `postId`
- `script`
- `scenes`
- `storagePath`
- `provider`
- `status`
- `createdAt`

### `seo_keywords`

Purpose: SEO keywords, blog ideas, FAQs, and metadata.

Fields:

- `businessId`
- `keyword`
- `intent`
- `score`
- `titleIdeas`
- `metaDescriptions`
- `faqs`
- `relatedProducts`
- `createdAt`

### `social_accounts`

Purpose: connected social profiles.

Fields:

- `businessId`
- `platform`
- `accountId`
- `displayName`
- `tokenRef`
- `permissions`
- `status`
- `connectedAt`
- `updatedAt`

Important: do not store raw long-lived secrets in ordinary documents if a safer secret manager is available.

### `scheduled_posts`

Purpose: scheduled or published social posts.

Fields:

- `businessId`
- `postId`
- `product_id`
- `product_name`
- `content_type`
- `caption`
- `hashtags`
- `poster_prompt`
- `platforms`
- `scheduledAt`
- `publishedAt`
- `platformPostId`
- `status`
- `errorMessage`
- `createdAt`
- `updatedAt`

Current implementation detail:

- Document path: `scheduled_posts/{scheduledPostId}`
- Each scheduled post stores `business_id` and a content snapshot from the approved generated post.
- Creating a scheduled post sets the source generated post status to `scheduled` and adds `scheduled_post_id` plus `scheduled_at`.
- Cancelling a scheduled post deletes the schedule document and returns the source generated post status to `approved`.
- Mock publishing sets `status` to `published`, stores `published_at` and `platform_post_id`, clears `error_message`, and marks the source generated post as `published`.
- Failed mock or future live publishing attempts can set `status` to `failed` and store `error_message`.

### `analytics`

Purpose: normalized performance metrics.

Fields:

- `businessId`
- `postId`
- `platform`
- `date`
- `reach`
- `likes`
- `comments`
- `shares`
- `saves`
- `clicks`
- `ctr`
- `ordersAttributed`
- `revenueAttributed`
- `updatedAt`

### `sales`

Purpose: sales records or aggregates used by product selection and recommendations.

Fields:

- `businessId`
- `productId`
- `date`
- `orders`
- `unitsSold`
- `revenue`
- `source`
- `campaignId`
- `createdAt`

### `recommendations`

Purpose: user-facing next actions.

Fields:

- `businessId`
- `title`
- `reason`
- `actionType`
- `priority`
- `relatedProductIds`
- `relatedPostIds`
- `status`
- `createdByRunId`
- `createdAt`

### `agent_logs`

Purpose: trace every agent run and decision.

Fields:

- `businessId`
- `runId`
- `agentName`
- `workflowName`
- `inputSummary`
- `outputSummary`
- `model`
- `status`
- `errorMessage`
- `startedAt`
- `finishedAt`

## Entity Relationships

```text
users
  -> businesses
      -> brand_profiles
      -> products
      -> trends
      -> competitors
      -> content_plans
          -> generated_posts
              -> generated_posters
              -> generated_videos
              -> scheduled_posts
                  -> analytics
      -> seo_keywords
      -> sales
      -> recommendations
      -> agent_logs
```

## Storage Paths

Planned Firebase Storage paths:

```text
businesses/{businessId}/product-images/{productId}/{fileName}
businesses/{businessId}/posters/{posterId}/{fileName}
businesses/{businessId}/videos/{videoId}/{fileName}
businesses/{businessId}/blogs/{blogId}/{fileName}
businesses/{businessId}/brand-assets/{fileName}
```

## Indexing Notes

Likely Firestore query patterns:

- Products by `businessId` and `isActive`.
- Content plans by `businessId`, `startDate`, and `endDate`.
- Generated posts by `businessId`, `status`, and `createdAt`.
- Scheduled posts by `businessId`, `status`, and `scheduledAt`.
- Analytics by `businessId`, `platform`, and `date`.
- Agent logs by `businessId`, `runId`, and `startedAt`.

Actual indexes:

- UNKNOWN - NEEDS VERIFICATION.

## Unknowns

- Exact nested versus top-level collection strategy.
- Whether sales data is imported manually, via CSV, or through ecommerce integration.
- Final storage access rules.
- Final retention period for logs and generated assets.

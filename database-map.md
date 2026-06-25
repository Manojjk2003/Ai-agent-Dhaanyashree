# Database Map

## Documentation Maintenance Rule

Update this file whenever Firestore collections, document fields, storage paths, indexes, relationships, or lifecycle rules change. If an API reads/writes the changed data, update `api-map.md` too.

## Current State

No database implementation exists yet. Firebase config placeholders and a backend Firebase service placeholder exist. This file defines the planned Firestore and Firebase Storage model.

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

- User can own or access one or more `businesses`.

### `businesses`

Purpose: top-level business entity.

Fields:

- `businessId`
- `ownerUserId`
- `name`
- `industry`
- `description`
- `goals`
- `createdAt`
- `updatedAt`

Relationships:

- Parent for products, brand profiles, content plans, analytics, recommendations, and logs.

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
- `imageUrls`
- `inventoryStatus`
- `targetAudience`
- `isActive`
- `createdAt`
- `updatedAt`

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
- `trendId`
- `contentType`
- `platforms`
- `caption`
- `cta`
- `hashtags`
- `status`
- `scheduledPostId`
- `createdByRunId`
- `createdAt`
- `updatedAt`

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

- `businessId`
- `postId`
- `prompt`
- `storagePath`
- `publicUrl`
- `provider`
- `status`
- `createdByRunId`
- `createdAt`

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
- `platform`
- `scheduledAt`
- `publishedAt`
- `platformPostId`
- `status`
- `errorMessage`
- `createdAt`
- `updatedAt`

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

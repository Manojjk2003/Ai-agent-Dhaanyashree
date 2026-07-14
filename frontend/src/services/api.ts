const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type RequestOptions = {
  token?: string;
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
};

async function request<T>(path: string, options: RequestOptions = {}) {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed: ${response.status}`);
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json() as Promise<T>;
}

export type BusinessProfile = {
  business_name: string;
  industry: string;
  description: string;
  target_audience: string[];
  brand_tone: string;
  goals: string[];
};

export type BusinessProfileResponse = BusinessProfile & {
  business_id: string;
  owner_user_id: string;
  updated: boolean;
};

export type ProductInput = {
  name: string;
  category: string;
  description: string;
  benefits: string[];
  ingredients: string[];
  price: number | null;
  target_audience: string[];
  image_url: string;
  is_active: boolean;
};

export type ProductResponse = ProductInput & {
  product_id: string;
  business_id: string;
};

export type DailyPlanResponse = {
  run_id: string;
  content_plan_id: string;
  post_id: string;
  poster_id: string | null;
  status: "ready_for_review" | "draft";
  summary: string;
  business_name: string;
  selected_product_id: string;
  selected_product_name: string;
  selection_reason: string;
  content_type: string;
  content_idea: string;
  caption: string;
  hashtags: string[];
  poster_prompt: string | null;
  generation_source: "gemini" | "fallback";
};

export type GeneratedPostStatus =
  | "draft"
  | "ready_for_review"
  | "approved"
  | "rejected"
  | "scheduled"
  | "published";

export type GeneratedPostResponse = {
  post_id: string;
  business_id: string;
  run_id: string;
  content_plan_id: string;
  product_id: string;
  product_name: string;
  selection_reason: string;
  content_type: string;
  content_idea: string;
  caption: string;
  hashtags: string[];
  poster_prompt: string | null;
  platforms: string[];
  run_date: string;
  status: GeneratedPostStatus;
  generation_source: "gemini" | "fallback";
  scheduled_post_id: string | null;
  scheduled_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ScheduledPostInput = {
  post_id: string;
  scheduled_at: string;
  platforms: string[];
};

export type ScheduleRecommendationInput = {
  post_id: string;
  target_date?: string;
  platforms: string[];
};

export type ScheduleRecommendationResponse = {
  recommended_at: string;
  reason: string;
  confidence: number;
  alternative_slots: string[];
  generation_source: "gemini" | "fallback";
};

export type ScheduledPostResponse = {
  scheduled_post_id: string;
  business_id: string;
  post_id: string;
  product_id: string;
  product_name: string;
  content_type: string;
  caption: string;
  hashtags: string[];
  poster_prompt: string | null;
  platforms: string[];
  scheduled_at: string;
  published_at: string | null;
  platform_post_id: string | null;
  error_message: string | null;
  status: "scheduled" | "published" | "cancelled" | "failed";
  created_at: string;
  updated_at: string;
};

export type PublishNowResponse = {
  scheduled_post: ScheduledPostResponse;
  provider: "mock" | "meta";
  platform_post_id: string;
  message: string;
};

export type GeneratedPosterResponse = {
  poster_id: string;
  business_id: string;
  post_id: string;
  product_id: string;
  product_name: string;
  prompt: string;
  image_url: string;
  storage_path: string;
  mime_type: string;
  provider: "gemini" | "huggingface" | "fallback";
  error_message: string | null;
  status: "generated";
  created_at: string;
  updated_at: string;
};

export async function getHealth() {
  return request<{ status: string; service: string }>("/health");
}

export async function getBusinessProfile(token: string) {
  return request<BusinessProfileResponse | null>("/business/profile", { token });
}

export async function saveBusinessProfile(
  token: string,
  profile: BusinessProfile,
) {
  return request<BusinessProfileResponse>("/business/profile", {
    token,
    method: "POST",
    body: profile,
  });
}

export async function listProducts(token: string) {
  return request<ProductResponse[]>("/products", { token });
}

export async function createProduct(token: string, product: ProductInput) {
  return request<ProductResponse>("/products", {
    token,
    method: "POST",
    body: product,
  });
}

export async function updateProduct(
  token: string,
  productId: string,
  product: Partial<ProductInput>,
) {
  return request<ProductResponse>(`/products/${productId}`, {
    token,
    method: "PATCH",
    body: product,
  });
}

export async function deleteProduct(token: string, productId: string) {
  return request<null>(`/products/${productId}`, {
    token,
    method: "DELETE",
  });
}

export async function runDailyPlan(token: string) {
  return request<DailyPlanResponse>("/agent/run-daily-plan", {
    token,
    method: "POST",
    body: {
      run_date: new Date().toISOString().slice(0, 10),
      platforms: ["instagram"],
      require_poster: true,
    },
  });
}

export async function listGeneratedPosts(token: string) {
  return request<GeneratedPostResponse[]>("/content/posts", { token });
}

export async function updateGeneratedPost(
  token: string,
  postId: string,
  post: Partial<Pick<GeneratedPostResponse, "caption" | "hashtags" | "poster_prompt" | "status">>,
) {
  return request<GeneratedPostResponse>(`/content/posts/${postId}`, {
    token,
    method: "PATCH",
    body: post,
  });
}

export async function deleteGeneratedPost(token: string, postId: string) {
  return request<null>(`/content/posts/${postId}`, {
    token,
    method: "DELETE",
  });
}

export async function listGeneratedPosters(token: string) {
  return request<GeneratedPosterResponse[]>("/posters", { token });
}

export async function generatePoster(token: string, postId: string) {
  return request<GeneratedPosterResponse>("/posters/generate", {
    token,
    method: "POST",
    body: {
      post_id: postId,
    },
  });
}

export async function listScheduledPosts(token: string) {
  return request<ScheduledPostResponse[]>("/schedule/posts", { token });
}

export async function createScheduledPost(
  token: string,
  scheduledPost: ScheduledPostInput,
) {
  return request<ScheduledPostResponse>("/schedule/posts", {
    token,
    method: "POST",
    body: scheduledPost,
  });
}

export async function recommendScheduleTime(
  token: string,
  recommendation: ScheduleRecommendationInput,
) {
  return request<ScheduleRecommendationResponse>("/schedule/recommend-time", {
    token,
    method: "POST",
    body: recommendation,
  });
}

export async function deleteScheduledPost(
  token: string,
  scheduledPostId: string,
) {
  return request<null>(`/schedule/posts/${scheduledPostId}`, {
    token,
    method: "DELETE",
  });
}

export async function publishScheduledPostNow(
  token: string,
  scheduledPostId: string,
) {
  return request<PublishNowResponse>("/social/publish-now", {
    token,
    method: "POST",
    body: {
      scheduled_post_id: scheduledPostId,
    },
  });
}

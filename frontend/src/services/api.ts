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

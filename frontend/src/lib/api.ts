/**
 * Base API Client for Nexus-Mind
 * Configures authentication, base URLs, and common error handling.
 */

// If we need a more robust solution, we can replace this with Axios, 
// but fetch is perfectly fine for clean architecture in modern Next.js.

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface RequestOptions extends RequestInit {
  requireAuth?: boolean;
}

export class ApiError extends Error {
  constructor(public status: number, public detail: any) {
    super(`API Error ${status}: ${JSON.stringify(detail)}`);
  }
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { requireAuth = true, headers = {}, ...customConfig } = options;

  const isFormData = customConfig.body instanceof FormData;

  const config: RequestInit = {
    ...customConfig,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...headers,
    },
  };

  // Extract auth token from wherever it's stored (localStorage for Client Components)
  if (requireAuth && typeof window !== "undefined") {
    const token = localStorage.getItem("nexus_access_token");
    if (token) {
      (config.headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    let errorDetail;
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || errorData.message || "Unknown Error";
    } catch {
      errorDetail = await response.text();
    }
    throw new ApiError(response.status, errorDetail);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const api = {
  get: <T>(endpoint: string, options?: RequestOptions) => 
    request<T>(endpoint, { ...options, method: "GET" }),
    
  post: <T>(endpoint: string, data: any, options?: RequestOptions) => 
    request<T>(endpoint, { 
      ...options, 
      method: "POST", 
      body: data instanceof FormData ? data : JSON.stringify(data)
    }),
    
  put: <T>(endpoint: string, data: any, options?: RequestOptions) => 
    request<T>(endpoint, { ...options, method: "PUT", body: JSON.stringify(data) }),
    
  delete: <T>(endpoint: string, options?: RequestOptions) => 
    request<T>(endpoint, { ...options, method: "DELETE" }),
};

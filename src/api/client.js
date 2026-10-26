/**
 * Base API client with configurable base URL and standardized request handling.
 */

const BASE_URL = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '');

export function getApiUrl(path) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${BASE_URL}${normalizedPath}`;
}

export async function apiClient(path, options = {}) {
  const url = getApiUrl(path);
  const headers = { ...options.headers };

  if (options.body && !(options.body instanceof FormData) && typeof options.body === 'object') {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  return response;
}

export async function apiJson(path, options = {}) {
  const response = await apiClient(path, options);
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData?.detail) {
        errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
      } else if (errorData?.error) {
        errorMessage = errorData.error;
      }
    } catch {
      // Ignore json parse error on response failure
    }
    const err = new Error(errorMessage);
    err.status = response.status;
    throw err;
  }
  return response.json();
}

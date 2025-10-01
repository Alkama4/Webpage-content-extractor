// fastapi.ts
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

interface RequestOptions {
  method?: HttpMethod;
  body?: Record<string, unknown>;
  headers?: HeadersInit; // e.g. { Authorization: 'Bearer ...' }
}

export async function apiRequest<T = unknown>(
  path: string,
  {
    method = 'GET',
    body,
    headers
  }: RequestOptions = {}
): Promise<T> {
  const url = `${'http://127.0.0.1:8000'}${path}`;

  const init: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(headers || {})
    }
  };

  if (body) {
    init.body = JSON.stringify(body);
  }

  const res = await fetch(url, init);

  // Throw on non‑2xx status
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${path} failed: ${res.status} – ${text}`);
  }

  // Clone the response so we can try JSON first and fall back to text.
  const resClone = res.clone();

  try {
    return (await res.json()) as T;
  } catch (_) {
    // If parsing JSON fails, read from the cloned copy
    return (await resClone.text()) as unknown as T;
  }
}
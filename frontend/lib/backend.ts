const BACKEND_BASE_URL = process.env.BACKEND_BASE_URL || 'http://backend:8000'

export function backendUrl(path: string): string {
  return `${BACKEND_BASE_URL}${path}`
}

export async function proxyJson(target: string, init?: RequestInit): Promise<Response> {
  const response = await fetch(target, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    cache: 'no-store',
  })

  const text = await response.text()
  return new Response(text, {
    status: response.status,
    headers: {
      'Content-Type': response.headers.get('content-type') || 'application/json',
    },
  })
}

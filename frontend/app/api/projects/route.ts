import { backendUrl, proxyJson } from '../../../lib/backend'

export async function GET(request: Request) {
  const { search } = new URL(request.url)
  return proxyJson(backendUrl(`/projects${search}`))
}

export async function POST(request: Request) {
  const body = await request.text()
  return proxyJson(backendUrl('/projects'), { method: 'POST', body })
}

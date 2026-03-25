import { backendUrl, proxyJson } from '../../../../lib/backend'

type Params = { params: Promise<{ id: string }> }

export async function GET(_request: Request, { params }: Params) {
  const { id } = await params
  return proxyJson(backendUrl(`/projects/${id}`))
}

export async function PUT(request: Request, { params }: Params) {
  const { id } = await params
  const body = await request.text()
  return proxyJson(backendUrl(`/projects/${id}`), { method: 'PUT', body })
}

export async function DELETE(_request: Request, { params }: Params) {
  const { id } = await params
  return proxyJson(backendUrl(`/projects/${id}`), { method: 'DELETE' })
}

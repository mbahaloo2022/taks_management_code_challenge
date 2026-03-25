import { backendUrl, proxyJson } from '../../../../../lib/backend'

type Params = { params: Promise<{ id: string }> }

export async function PATCH(_request: Request, { params }: Params) {
  const { id } = await params
  return proxyJson(backendUrl(`/tasks/${id}/complete`), { method: 'PATCH' })
}

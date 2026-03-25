import { backendUrl, proxyJson } from '../../../../../../../lib/backend'

type Params = { params: Promise<{ projectId: string; taskId: string }> }

export async function POST(_request: Request, { params }: Params) {
  const { projectId, taskId } = await params
  return proxyJson(backendUrl(`/projects/${projectId}/tasks/${taskId}/link`), { method: 'POST' })
}

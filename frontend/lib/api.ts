export const API_BASE = '/api'

export type Task = {
  id: string
  project_id: string | null
  title: string
  description: string | null
  deadline: string
  completed: boolean
  created_at?: string
  updated_at?: string
}

export type Project = {
  id: string
  title: string
  deadline: string
  completed: boolean
  created_at?: string
  updated_at?: string
}

export type PaginatedResponse<T> = {
  items: T[]
  total: number
  limit: number
  offset: number
}

export type ConflictError = Error & { status?: number; detail?: string; incomplete_task_ids?: string[] }

async function parseResponse<T>(res: Response): Promise<T> {
  if (res.ok) {
    if (res.status === 204) {
      return undefined as T
    }
    return (await res.json()) as T
  }

  let payload: Record<string, unknown> = {}
  try {
    payload = (await res.json()) as Record<string, unknown>
  } catch {
    // ignore body parse errors
  }

  const error = new Error(String(payload.detail ?? 'Request failed')) as ConflictError
  error.status = res.status
  error.detail = typeof payload.detail === 'string' ? payload.detail : 'Request failed'
  if (Array.isArray(payload.incomplete_task_ids)) {
    error.incomplete_task_ids = payload.incomplete_task_ids as string[]
  }
  throw error
}

function qs(params: Record<string, string | number | boolean | undefined | null>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value))
    }
  }
  const query = search.toString()
  return query ? `?${query}` : ''
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    cache: 'no-store',
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })
  return parseResponse<T>(res)
}

export async function listTasks(filters?: {
  completed?: boolean
  overdue?: boolean
  project_id?: string
  limit?: number
  offset?: number
}): Promise<PaginatedResponse<Task>> {
  return request<PaginatedResponse<Task>>(`/tasks${qs(filters ?? {})}`)
}

export async function getTask(taskId: string): Promise<Task> {
  return request<Task>(`/tasks/${taskId}`)
}

export async function createTask(payload: {
  title: string
  description?: string | null
  deadline: string
  project_id?: string | null
}): Promise<Task> {
  return request<Task>('/tasks', { method: 'POST', body: JSON.stringify(payload) })
}

export async function updateTask(
  taskId: string,
  payload: {
    title?: string | null
    description?: string | null
    deadline?: string | null
    completed?: boolean | null
    project_id?: string | null
  },
): Promise<Task> {
  return request<Task>(`/tasks/${taskId}`, { method: 'PUT', body: JSON.stringify(payload) })
}

export async function deleteTask(taskId: string): Promise<void> {
  return request<void>(`/tasks/${taskId}`, { method: 'DELETE' })
}

export async function completeTask(taskId: string): Promise<Task> {
  return request<Task>(`/tasks/${taskId}/complete`, { method: 'PATCH' })
}

export async function listProjects(filters?: { limit?: number; offset?: number }): Promise<PaginatedResponse<Project>> {
  return request<PaginatedResponse<Project>>(`/projects${qs(filters ?? {})}`)
}

export async function getProject(projectId: string): Promise<Project> {
  return request<Project>(`/projects/${projectId}`)
}

export async function createProject(payload: { title: string; deadline: string }): Promise<Project> {
  return request<Project>('/projects', { method: 'POST', body: JSON.stringify(payload) })
}

export async function updateProject(
  projectId: string,
  payload: { title?: string | null; deadline?: string | null; completed?: boolean | null },
): Promise<Project> {
  return request<Project>(`/projects/${projectId}`, { method: 'PUT', body: JSON.stringify(payload) })
}

export async function deleteProject(projectId: string): Promise<void> {
  return request<void>(`/projects/${projectId}`, { method: 'DELETE' })
}

export async function listProjectTasks(projectId: string): Promise<Task[]> {
  return request<Task[]>(`/projects/${projectId}/tasks`)
}

export async function linkTaskToProject(projectId: string, taskId: string): Promise<Task> {
  return request<Task>(`/projects/${projectId}/tasks/${taskId}/link`, { method: 'POST' })
}

export async function unlinkTaskFromProject(projectId: string, taskId: string): Promise<Task> {
  return request<Task>(`/projects/${projectId}/tasks/${taskId}/unlink`, { method: 'DELETE' })
}

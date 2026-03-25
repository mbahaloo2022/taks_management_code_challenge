import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import { Dashboard } from '../components/dashboard'

const api = {
  listTasks: vi.fn(),
  listProjects: vi.fn(),
  getTask: vi.fn(),
  getProject: vi.fn(),
  listProjectTasks: vi.fn(),
  createTask: vi.fn(),
  updateTask: vi.fn(),
  deleteTask: vi.fn(),
  completeTask: vi.fn(),
  createProject: vi.fn(),
  updateProject: vi.fn(),
  deleteProject: vi.fn(),
  linkTaskToProject: vi.fn(),
  unlinkTaskFromProject: vi.fn(),
}

vi.mock('../lib/api', () => api)

beforeEach(() => {
  vi.clearAllMocks()
  api.listTasks.mockResolvedValue({ items: [{ id: 't1', title: 'Demo task', description: null, deadline: '2026-03-25T10:00:00Z', completed: false, project_id: null }], total: 1, limit: 20, offset: 0 })
  api.listProjects.mockResolvedValue({ items: [{ id: 'p1', title: 'Demo project', deadline: '2026-03-30T10:00:00Z', completed: false }], total: 1, limit: 20, offset: 0 })
  api.createTask.mockResolvedValue({ id: 't2', title: 'Created task', description: null, deadline: '2026-03-26T10:00:00Z', completed: false, project_id: null })
  api.getProject.mockResolvedValue({ id: 'p1', title: 'Demo project', deadline: '2026-03-30T10:00:00Z', completed: false })
  api.listProjectTasks.mockResolvedValue([])
})

test('loads dashboard data and creates a task', async () => {
  render(<Dashboard />)

  expect(await screen.findByText('Demo task')).toBeInTheDocument()
  expect(await screen.findByText('Demo project')).toBeInTheDocument()

  fireEvent.change(screen.getByLabelText('Task title'), { target: { value: 'New task', name: 'title' } })
  fireEvent.change(screen.getByLabelText('Task deadline'), { target: { value: '2026-03-25T12:00', name: 'deadline' } })
  fireEvent.click(screen.getByRole('button', { name: 'Create task' }))

  await waitFor(() => expect(api.createTask).toHaveBeenCalled())
})

test('loads selected project details', async () => {
  render(<Dashboard />)
  const getButtons = await screen.findAllByRole('button', { name: 'Get' })
  fireEvent.click(getButtons[1])
  await waitFor(() => expect(api.getProject).toHaveBeenCalledWith('p1'))
})

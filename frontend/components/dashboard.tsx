'use client'

import { useEffect, useMemo, useState } from 'react'
import type { CSSProperties, ChangeEvent, FormEvent } from 'react'
import {
  completeTask,
  createProject,
  createTask,
  deleteProject,
  deleteTask,
  getProject,
  getTask,
  linkTaskToProject,
  listProjects,
  listProjectTasks,
  listTasks,
  type Project,
  type Task,
  unlinkTaskFromProject,
  updateProject,
  updateTask,
} from '../lib/api'

const pageStyle: CSSProperties = {
  fontFamily: 'Inter, Arial, sans-serif',
  color: '#132238',
  padding: '24px',
}

const gridStyle: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '1.15fr 1fr',
  gap: '20px',
  alignItems: 'start',
}

const cardStyle: CSSProperties = {
  background: '#fff',
  borderRadius: 16,
  padding: 18,
  boxShadow: '0 8px 30px rgba(16, 24, 40, 0.08)',
  border: '1px solid #e7ecf3',
}

const inputStyle: CSSProperties = {
  width: '100%',
  boxSizing: 'border-box',
  padding: '10px 12px',
  borderRadius: 10,
  border: '1px solid #c7d2e2',
  fontSize: 14,
  marginTop: 6,
}

const buttonStyle: CSSProperties = {
  borderRadius: 10,
  border: '1px solid #cad4e4',
  background: '#fff',
  padding: '8px 12px',
  cursor: 'pointer',
  fontWeight: 600,
}

const primaryButtonStyle: CSSProperties = {
  ...buttonStyle,
  background: '#155eef',
  color: '#fff',
  borderColor: '#155eef',
}

type TaskFormState = {
  title: string
  description: string
  deadline: string
  project_id: string
}

type ProjectFormState = {
  title: string
  deadline: string
}

type Filters = {
  completed: 'all' | 'true' | 'false'
  overdue: 'all' | 'true' | 'false'
  project_id: string
}

const initialTaskForm: TaskFormState = {
  title: '',
  description: '',
  deadline: '',
  project_id: '',
}

const initialProjectForm: ProjectFormState = {
  title: '',
  deadline: '',
}

function toApiDate(value: string): string {
  if (!value) return value
  return value.includes('T') && !value.endsWith('Z') ? new Date(value).toISOString() : value
}

function toInputDate(value?: string | null): string {
  if (!value) return ''
  const d = new Date(value)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function fmt(value?: string | null): string {
  if (!value) return '—'
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

export function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [selectedProjectTasks, setSelectedProjectTasks] = useState<Task[]>([])
  const [taskForm, setTaskForm] = useState<TaskFormState>(initialTaskForm)
  const [projectForm, setProjectForm] = useState<ProjectFormState>(initialProjectForm)
  const [filters, setFilters] = useState<Filters>({ completed: 'all', overdue: 'all', project_id: '' })
  const [taskLoading, setTaskLoading] = useState(false)
  const [projectLoading, setProjectLoading] = useState(false)
  const [message, setMessage] = useState<string>('')
  const [error, setError] = useState<string>('')

  const openTaskCount = useMemo(() => tasks.filter((task) => !task.completed).length, [tasks])

  async function refreshTasks(nextFilters: Filters = filters) {
    const page = await listTasks({
      completed: nextFilters.completed === 'all' ? undefined : nextFilters.completed === 'true',
      overdue: nextFilters.overdue === 'all' ? undefined : nextFilters.overdue === 'true',
      project_id: nextFilters.project_id || undefined,
    })
    setTasks(page.items)
  }

  async function refreshProjects() {
    const page = await listProjects()
    setProjects(page.items)
  }

  async function bootstrap() {
    setTaskLoading(true)
    setProjectLoading(true)
    setError('')
    try {
      await Promise.all([refreshTasks(filters), refreshProjects()])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setTaskLoading(false)
      setProjectLoading(false)
    }
  }

  useEffect(() => {
    void bootstrap()
  }, [])

  function clearFlash() {
    setMessage('')
    setError('')
  }

  function onTaskFormChange(event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value } = event.target
    setTaskForm((prev) => ({ ...prev, [name]: value }))
  }

  function onProjectFormChange(event: ChangeEvent<HTMLInputElement>) {
    const { name, value } = event.target
    setProjectForm((prev) => ({ ...prev, [name]: value }))
  }

  async function submitTask(event: FormEvent) {
    event.preventDefault()
    clearFlash()
    try {
      if (selectedTask) {
        const updated = await updateTask(selectedTask.id, {
          title: taskForm.title,
          description: taskForm.description || null,
          deadline: toApiDate(taskForm.deadline),
          project_id: taskForm.project_id || null,
        })
        setSelectedTask(updated)
        setMessage('Task updated.')
      } else {
        const created = await createTask({
          title: taskForm.title,
          description: taskForm.description || null,
          deadline: toApiDate(taskForm.deadline),
          project_id: taskForm.project_id || null,
        })
        setSelectedTask(created)
        setMessage('Task created.')
      }
      setTaskForm(initialTaskForm)
      setSelectedTask(null)
      await Promise.all([refreshTasks(), refreshProjects()])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Task request failed')
    }
  }

  async function submitProject(event: FormEvent) {
    event.preventDefault()
    clearFlash()
    try {
      if (selectedProject) {
        const updated = await updateProject(selectedProject.id, {
          title: projectForm.title,
          deadline: toApiDate(projectForm.deadline),
        })
        setSelectedProject(updated)
        setMessage('Project updated.')
      } else {
        const created = await createProject({
          title: projectForm.title,
          deadline: toApiDate(projectForm.deadline),
        })
        setSelectedProject(created)
        setMessage('Project created.')
      }
      setProjectForm(initialProjectForm)
      setSelectedProject(null)
      await refreshProjects()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Project request failed')
    }
  }

  async function handleGetTask(taskId: string) {
    clearFlash()
    try {
      const task = await getTask(taskId)
      setSelectedTask(task)
      setTaskForm({
        title: task.title,
        description: task.description ?? '',
        deadline: toInputDate(task.deadline),
        project_id: task.project_id ?? '',
      })
      setMessage(`Loaded task ${task.title}.`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load task')
    }
  }

  async function handleGetProject(projectId: string) {
    clearFlash()
    try {
      const [project, projectTasks] = await Promise.all([getProject(projectId), listProjectTasks(projectId)])
      setSelectedProject(project)
      setSelectedProjectTasks(projectTasks)
      setProjectForm({ title: project.title, deadline: toInputDate(project.deadline) })
      setMessage(`Loaded project ${project.title}.`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load project')
    }
  }

  async function toggleTaskCompletion(task: Task) {
    clearFlash()
    try {
      if (task.completed) {
        await updateTask(task.id, { completed: false })
        setMessage('Task reopened.')
      } else {
        await completeTask(task.id)
        setMessage('Task completed.')
      }
      await Promise.all([refreshTasks(), refreshProjects(), selectedProject ? handleGetProject(selectedProject.id) : Promise.resolve()])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to change task completion')
    }
  }

  async function toggleProjectCompletion(project: Project) {
    clearFlash()
    try {
      await updateProject(project.id, { completed: !project.completed })
      setMessage(project.completed ? 'Project reopened.' : 'Project completed.')
      await Promise.all([refreshProjects(), selectedProject?.id === project.id ? handleGetProject(project.id) : Promise.resolve()])
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to change project completion')
      }
    }
  }

  async function handleDeleteTask(taskId: string) {
    clearFlash()
    try {
      await deleteTask(taskId)
      if (selectedTask?.id === taskId) {
        setSelectedTask(null)
        setTaskForm(initialTaskForm)
      }
      setMessage('Task deleted.')
      await Promise.all([refreshTasks(), refreshProjects(), selectedProject ? handleGetProject(selectedProject.id) : Promise.resolve()])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task')
    }
  }

  async function handleDeleteProject(projectId: string) {
    clearFlash()
    try {
      await deleteProject(projectId)
      if (selectedProject?.id === projectId) {
        setSelectedProject(null)
        setSelectedProjectTasks([])
        setProjectForm(initialProjectForm)
      }
      setMessage('Project deleted.')
      await Promise.all([refreshProjects(), refreshTasks()])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete project')
    }
  }

  async function handleLink(taskId: string, projectId: string) {
    clearFlash()
    try {
      await linkTaskToProject(projectId, taskId)
      setMessage('Task linked to project.')
      await Promise.all([refreshTasks(), refreshProjects(), handleGetProject(projectId)])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to link task')
    }
  }

  async function handleUnlink(task: Task) {
    clearFlash()
    if (!task.project_id) return
    try {
      await unlinkTaskFromProject(task.project_id, task.id)
      setMessage('Task unlinked from project.')
      await Promise.all([refreshTasks(), refreshProjects(), selectedProject ? handleGetProject(selectedProject.id) : Promise.resolve()])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to unlink task')
    }
  }

  async function applyFilters(next: Partial<Filters>) {
    const nextFilters = { ...filters, ...next }
    setFilters(nextFilters)
    clearFlash()
    try {
      await refreshTasks(nextFilters)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to apply filters')
    }
  }

  return (
    <main style={pageStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center', marginBottom: 18 }}>
        <div>
          <h1 style={{ margin: 0 }}>Tasks & Projects Dashboard</h1>
          <p style={{ margin: '6px 0 0', color: '#516076' }}>Full frontend coverage for all challenge APIs.</p>
        </div>
        <button type="button" style={buttonStyle} onClick={() => void bootstrap()}>
          Refresh all
        </button>
      </div>

      {(message || error) && (
        <div
          role={error ? 'alert' : 'status'}
          style={{
            ...cardStyle,
            marginBottom: 16,
            borderColor: error ? '#f0b6b6' : '#b8d7ff',
            background: error ? '#fff4f4' : '#f4f8ff',
          }}
        >
          {error || message}
        </div>
      )}

      <div style={gridStyle}>
        <section style={{ display: 'grid', gap: 20 }}>
          <div style={cardStyle}>
            <h2 style={{ marginTop: 0 }}>{selectedTask ? 'Edit task' : 'Create task'}</h2>
            <form onSubmit={(event) => void submitTask(event)}>
              <label>
                Title
                <input aria-label="Task title" name="title" required style={inputStyle} value={taskForm.title} onChange={onTaskFormChange} />
              </label>
              <label>
                Description
                <textarea aria-label="Task description" name="description" style={{ ...inputStyle, minHeight: 90 }} value={taskForm.description} onChange={onTaskFormChange} />
              </label>
              <label>
                Deadline
                <input aria-label="Task deadline" name="deadline" required type="datetime-local" style={inputStyle} value={taskForm.deadline} onChange={onTaskFormChange} />
              </label>
              <label>
                Project
                <select aria-label="Task project" name="project_id" style={inputStyle} value={taskForm.project_id} onChange={onTaskFormChange}>
                  <option value="">No project</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>{project.title}</option>
                  ))}
                </select>
              </label>
              <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
                <button style={primaryButtonStyle} type="submit">{selectedTask ? 'Save task' : 'Create task'}</button>
                <button type="button" style={buttonStyle} onClick={() => { setSelectedTask(null); setTaskForm(initialTaskForm) }}>Clear</button>
              </div>
            </form>
          </div>

          <div style={cardStyle}>
            <h2 style={{ marginTop: 0 }}>{selectedProject ? 'Edit project' : 'Create project'}</h2>
            <form onSubmit={(event) => void submitProject(event)}>
              <label>
                Title
                <input aria-label="Project title" name="title" required style={inputStyle} value={projectForm.title} onChange={onProjectFormChange} />
              </label>
              <label>
                Deadline
                <input aria-label="Project deadline" name="deadline" required type="datetime-local" style={inputStyle} value={projectForm.deadline} onChange={onProjectFormChange} />
              </label>
              <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
                <button style={primaryButtonStyle} type="submit">{selectedProject ? 'Save project' : 'Create project'}</button>
                <button type="button" style={buttonStyle} onClick={() => { setSelectedProject(null); setSelectedProjectTasks([]); setProjectForm(initialProjectForm) }}>Clear</button>
              </div>
            </form>
          </div>
        </section>

        <section style={{ display: 'grid', gap: 20 }}>
          <div style={cardStyle}>
            <h2 style={{ marginTop: 0 }}>Task filters</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr auto', gap: 10 }}>
              <select aria-label="Completed filter" style={inputStyle} value={filters.completed} onChange={(e) => void applyFilters({ completed: e.target.value as Filters['completed'] })}>
                <option value="all">All completion states</option>
                <option value="true">Completed only</option>
                <option value="false">Open only</option>
              </select>
              <select aria-label="Overdue filter" style={inputStyle} value={filters.overdue} onChange={(e) => void applyFilters({ overdue: e.target.value as Filters['overdue'] })}>
                <option value="all">All deadlines</option>
                <option value="true">Overdue only</option>
                <option value="false">Not overdue only</option>
              </select>
              <select aria-label="Project filter" style={inputStyle} value={filters.project_id} onChange={(e) => void applyFilters({ project_id: e.target.value })}>
                <option value="">All projects</option>
                {projects.map((project) => <option key={project.id} value={project.id}>{project.title}</option>)}
              </select>
              <button type="button" style={buttonStyle} onClick={() => void applyFilters({ completed: 'all', overdue: 'all', project_id: '' })}>Reset</button>
            </div>
          </div>

          <div style={cardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ margin: 0 }}>Tasks</h2>
                <p style={{ margin: '6px 0 0', color: '#667085' }}>{taskLoading ? 'Loading…' : `${tasks.length} loaded, ${openTaskCount} open`}</p>
              </div>
            </div>
            <div style={{ display: 'grid', gap: 12, marginTop: 14 }}>
              {tasks.map((task) => (
                <article key={task.id} style={{ border: '1px solid #e6ebf2', borderRadius: 14, padding: 14 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                    <div>
                      <strong>{task.title}</strong>
                      <div style={{ color: '#667085', fontSize: 14, marginTop: 4 }}>{task.description || 'No description'}</div>
                    </div>
                    <span style={{ fontSize: 12, fontWeight: 700 }}>{task.completed ? 'COMPLETED' : 'OPEN'}</span>
                  </div>
                  <div style={{ marginTop: 10, fontSize: 14, color: '#516076' }}>
                    Deadline: {fmt(task.deadline)} · Project: {projects.find((project) => project.id === task.project_id)?.title ?? 'None'}
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 12 }}>
                    <button type="button" style={buttonStyle} onClick={() => void handleGetTask(task.id)}>Get</button>
                    <button type="button" style={buttonStyle} onClick={() => void toggleTaskCompletion(task)}>{task.completed ? 'Reopen' : 'Complete'}</button>
                    {task.project_id ? (
                      <button type="button" style={buttonStyle} onClick={() => void handleUnlink(task)}>Unlink</button>
                    ) : (
                      <select aria-label={`Link task ${task.title}`} style={{ ...inputStyle, width: 180, marginTop: 0 }} defaultValue="" onChange={(e) => e.target.value && void handleLink(task.id, e.target.value)}>
                        <option value="">Link to project</option>
                        {projects.map((project) => <option key={project.id} value={project.id}>{project.title}</option>)}
                      </select>
                    )}
                    <button type="button" style={buttonStyle} onClick={() => void handleDeleteTask(task.id)}>Delete</button>
                  </div>
                </article>
              ))}
              {!tasks.length && <p style={{ color: '#667085' }}>No tasks matched the selected filters.</p>}
            </div>
          </div>

          <div style={cardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ margin: 0 }}>Projects</h2>
                <p style={{ margin: '6px 0 0', color: '#667085' }}>{projectLoading ? 'Loading…' : `${projects.length} loaded`}</p>
              </div>
            </div>
            <div style={{ display: 'grid', gap: 12, marginTop: 14 }}>
              {projects.map((project) => (
                <article key={project.id} style={{ border: '1px solid #e6ebf2', borderRadius: 14, padding: 14 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                    <div>
                      <strong>{project.title}</strong>
                      <div style={{ color: '#516076', fontSize: 14, marginTop: 4 }}>Deadline: {fmt(project.deadline)}</div>
                    </div>
                    <span style={{ fontSize: 12, fontWeight: 700 }}>{project.completed ? 'COMPLETED' : 'OPEN'}</span>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 12 }}>
                    <button type="button" style={buttonStyle} onClick={() => void handleGetProject(project.id)}>Get</button>
                    <button type="button" style={buttonStyle} onClick={() => void toggleProjectCompletion(project)}>{project.completed ? 'Reopen' : 'Complete'}</button>
                    <button type="button" style={buttonStyle} onClick={() => void handleDeleteProject(project.id)}>Delete</button>
                  </div>
                </article>
              ))}
              {!projects.length && <p style={{ color: '#667085' }}>No projects yet.</p>}
            </div>
          </div>
        </section>
      </div>

      <section style={{ ...cardStyle, marginTop: 20 }}>
        <h2 style={{ marginTop: 0 }}>Selected project tasks</h2>
        {selectedProject ? (
          <>
            <p style={{ color: '#516076' }}>
              {selectedProject.title} · {selectedProjectTasks.length} task(s)
            </p>
            <ul style={{ paddingLeft: 20 }}>
              {selectedProjectTasks.map((task) => (
                <li key={task.id}>
                  {task.title} — {task.completed ? 'done' : 'open'} — deadline {fmt(task.deadline)}
                </li>
              ))}
            </ul>
            {!selectedProjectTasks.length && <p style={{ color: '#667085' }}>This project currently has no linked tasks.</p>}
          </>
        ) : (
          <p style={{ color: '#667085' }}>Choose a project using the Get button to load its details and task list.</p>
        )}
      </section>
    </main>
  )
}

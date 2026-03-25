import type { Task } from '../lib/api'

export function TaskList({ tasks }: { tasks: Task[] }) {
  return (
    <ul>
      {tasks.map((task) => (
        <li key={task.id}>
          <strong>{task.title}</strong> - {task.completed ? 'done' : 'open'}
        </li>
      ))}
    </ul>
  )
}

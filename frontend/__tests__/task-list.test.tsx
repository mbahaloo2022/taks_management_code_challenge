import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { TaskList } from '../components/task-list'

describe('TaskList', () => {
  it('renders task titles and statuses', () => {
    render(
      <TaskList
        tasks={[
          { id: '1', project_id: null, title: 'Write docs', description: null, deadline: new Date().toISOString(), completed: false },
          { id: '2', project_id: null, title: 'Ship feature', description: null, deadline: new Date().toISOString(), completed: true }
        ]}
      />
    )

    expect(screen.getByText('Write docs')).toBeInTheDocument()
    expect(screen.getByText('Ship feature')).toBeInTheDocument()
  })
})

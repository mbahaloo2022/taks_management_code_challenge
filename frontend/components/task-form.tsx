'use client'

import { useState } from 'react'

type Props = {
  onCreate: (payload: { title: string; deadline: string }) => Promise<void>
}

export function TaskForm({ onCreate }: Props) {
  const [title, setTitle] = useState('')
  const [deadline, setDeadline] = useState('')

  return (
    <form
      onSubmit={async (event) => {
        event.preventDefault()
        await onCreate({ title, deadline })
        setTitle('')
        setDeadline('')
      }}
    >
      <input aria-label="Task title" value={title} onChange={(e) => setTitle(e.target.value)} />
      <input aria-label="Task deadline" type="datetime-local" value={deadline} onChange={(e) => setDeadline(e.target.value)} />
      <button type="submit">Create task</button>
    </form>
  )
}

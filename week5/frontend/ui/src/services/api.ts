import type { ActionItem, ActionItemCreate, Note, NoteCreate } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${url}`, options);

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || `HTTP ${res.status}: ${res.statusText}`);
  }

  return res.json();
}

// Notes API
export const notesApi = {
  list: () => fetchJSON<Note[]>('/notes/'),

  create: (note: NoteCreate) =>
    fetchJSON<Note>('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(note),
    }),

  get: (id: number) => fetchJSON<Note>(`/notes/${id}`),

  search: (query: string) =>
    fetchJSON<Note[]>(`/notes/search?q=${encodeURIComponent(query)}`),
};

// Action Items API
export const actionItemsApi = {
  list: () => fetchJSON<ActionItem[]>('/action-items/'),

  create: (item: ActionItemCreate) =>
    fetchJSON<ActionItem>('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(item),
    }),

  complete: (id: number) =>
    fetchJSON<ActionItem>(`/action-items/${id}/complete`, {
      method: 'PUT',
    }),
};

import type {
  ActionItem,
  ActionItemBulkCompleteRequest,
  ActionItemBulkCompleteResponse,
  ActionItemCreate,
  Note,
  NoteCreate,
  NoteUpdate,
  PaginatedResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${url}`, options);

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || `HTTP ${res.status}: ${res.statusText}`);
  }

  // Handle 204 No Content (DELETE)
  if (res.status === 204) {
    return undefined as T;
  }

  return res.json();
}

// Notes API
export const notesApi = {
  list: (tagId?: number) => {
    const url = tagId === undefined
      ? '/notes/'
      : `/notes/?tag_id=${tagId}`;
    return fetchJSON<PaginatedResponse<Note>>(url);
  },

  create: (note: NoteCreate) =>
    fetchJSON<Note>('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(note),
    }),

  get: (id: number) => fetchJSON<Note>(`/notes/${id}`),

  update: (id: number, note: NoteUpdate) =>
    fetchJSON<Note>(`/notes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(note),
    }),

  delete: (id: number) =>
    fetchJSON<void>(`/notes/${id}`, {
      method: 'DELETE',
    }),

  search: (query: string, page = 1, pageSize = 10, sort = 'created_desc') =>
    fetchJSON<PaginatedResponse<Note>>(
      `/notes/search/?q=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}&sort=${sort}`
    ),
};

// Action Items API
export const actionItemsApi = {
  list: (completed?: boolean) => {
    const url = completed === undefined
      ? '/action-items/'
      : `/action-items/?completed=${completed}`;
    return fetchJSON<PaginatedResponse<ActionItem>>(url);
  },

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

  bulkComplete: (request: ActionItemBulkCompleteRequest) =>
    fetchJSON<ActionItemBulkCompleteResponse>('/action-items/bulk-complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    }),
};

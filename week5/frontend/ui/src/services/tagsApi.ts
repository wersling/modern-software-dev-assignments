import type { Note, Tag } from '../types';

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

/**
 * Tags API Service
 *
 * Provides methods for managing tags and their relationships with notes.
 */
export const tagsApi = {
  /**
   * Get all tags, optionally filtered by search query
   *
   * @param search - Optional search string to filter tags by name
   * @returns Promise<Tag[]> - Array of tags
   */
  list: (search?: string): Promise<Tag[]> => {
    const url = search
      ? `/tags/?search=${encodeURIComponent(search)}`
      : '/tags/';
    return fetchJSON<Tag[]>(url);
  },

  /**
   * Create a new tag
   *
   * @param name - The name of the tag to create
   * @returns Promise<Tag> - The created tag
   */
  create: (name: string): Promise<Tag> =>
    fetchJSON<Tag>('/tags/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    }),

  /**
   * Delete a tag by ID
   *
   * @param tagId - The ID of the tag to delete
   * @returns Promise<void>
   */
  delete: (tagId: number): Promise<void> =>
    fetchJSON<void>(`/tags/${tagId}`, {
      method: 'DELETE',
    }),

  /**
   * Attach multiple tags to a note
   *
   * @param noteId - The ID of the note
   * @param tagIds - Array of tag IDs to attach
   * @returns Promise<Note> - The updated note with tags
   */
  attachToNote: (noteId: number, tagIds: number[]): Promise<Note> =>
    fetchJSON<Note>(`/notes/${noteId}/tags`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tag_ids: tagIds }),
    }),

  /**
   * Remove a tag from a note
   *
   * @param noteId - The ID of the note
   * @param tagId - The ID of the tag to remove
   * @returns Promise<Note> - The updated note with remaining tags
   */
  removeFromNote: (noteId: number, tagId: number): Promise<Note> =>
    fetchJSON<Note>(`/notes/${noteId}/tags/${tagId}`, {
      method: 'DELETE',
    }),
};

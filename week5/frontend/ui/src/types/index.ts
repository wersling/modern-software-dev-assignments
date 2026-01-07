// Types matching backend Pydantic models
export interface Note {
  id: number;
  title: string;
  content: string;
  created_at: string;
}

export interface NoteCreate {
  title: string;
  content: string;
}

export interface NoteUpdate {
  title?: string;
  content?: string;
}

export interface ActionItem {
  id: number;
  description: string;
  completed: boolean;
  created_at: string;
}

export interface ActionItemCreate {
  description: string;
}

// API response wrapper
export interface ApiResponse<T> {
  data: T;
  error?: string;
}

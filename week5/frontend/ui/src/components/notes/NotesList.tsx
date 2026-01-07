import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { notesApi } from '../../services/api';
import type { Note, NoteUpdate } from '../../types';
import { NoteCard } from './NoteCard';
import { NoteForm } from './NoteForm';

export function NotesList() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadNotes = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await notesApi.list();
      setNotes(data);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load notes';
      setError(errorMsg);
      toast.error(errorMsg);
      console.error('Failed to load notes:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadNotes();
  }, []);

  const handleCreateNote = async (noteCreate: { title: string; content: string }) => {
    // Optimistic update - immediately add the note to the list
    const tempId = Date.now();
    const tempNote: Note = {
      id: tempId,
      ...noteCreate,
      created_at: new Date().toISOString(),
    };

    setNotes((prev) => [...prev, tempNote]);

    try {
      const createdNote = await notesApi.create(noteCreate);
      // Replace the temporary note with the real one from the server
      setNotes((prev) =>
        prev.map((note) => (note.id === tempId ? createdNote : note))
      );
    } catch (error) {
      // Rollback on error
      setNotes((prev) => prev.filter((note) => note.id !== tempId));
      throw error;
    }
  };

  const handleUpdateNote = async (id: number, data: NoteUpdate) => {
    // Optimistic update - immediately update the note in the list
    const previousNotes = [...notes];

    setNotes((prev) =>
      prev.map((note) =>
        note.id === id
          ? { ...note, ...(data.title && { title: data.title }), ...(data.content && { content: data.content }) }
          : note
      )
    );

    try {
      await notesApi.update(id, data);
    } catch (error) {
      // Rollback on error
      setNotes(previousNotes);
      throw error;
    }
  };

  const handleDeleteNote = async (id: number) => {
    // Optimistic update - immediately remove the note from the list
    const previousNotes = [...notes];
    setNotes((prev) => prev.filter((note) => note.id !== id));

    try {
      await notesApi.delete(id);
    } catch (error) {
      // Rollback on error
      setNotes(previousNotes);
      throw error;
    }
  };

  if (isLoading) {
    return <div>Loading notes...</div>;
  }

  if (error) {
    return (
      <div>
        <p>Error: {error}</p>
        <button onClick={loadNotes} type="button" className="btn-primary">
          Retry
        </button>
      </div>
    );
  }

  return (
    <section className="notes-section">
      <h2>Notes</h2>
      <NoteForm onSubmit={handleCreateNote} />
      {notes.length === 0 ? (
        <p>No notes yet. Create one above!</p>
      ) : (
        <ul className="notes-list">
          {notes.map((note) => (
            <NoteCard
              key={note.id}
              note={note}
              onUpdate={handleUpdateNote}
              onDelete={handleDeleteNote}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

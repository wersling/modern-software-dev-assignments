/**
 * Example: Implementing Tag Filtering in NotesList
 *
 * This example shows how to extend NotesList to support tag filtering
 * using the onTagClick callback from NoteCard component.
 */

import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { notesApi } from '../../services/api';
import type { Note, NoteUpdate } from '../../types';
import { NoteCard } from './NoteCard';
import { NoteForm } from './NoteForm';

export function NotesListWithTagFilter() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const pageSize = 10;

  useEffect(() => {
    const abortController = new AbortController();

    const loadNotes = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // If a tag is selected, we need to filter by that tag
        // This is a simple client-side filter example
        let data;
        if (selectedTag) {
          // Get all notes and filter by tag
          const allNotes = await notesApi.list();
          const filteredNotes = allNotes.filter(note =>
            note.tags.some(tag => tag.name === selectedTag)
          );
          data = {
            items: filteredNotes,
            total: filteredNotes.length,
            page: 1,
            page_size: pageSize
          };
        } else {
          // Normal search or list all
          data = searchQuery
            ? await notesApi.search(searchQuery, currentPage, pageSize)
            : { items: await notesApi.list(), total: 0, page: 1, page_size: pageSize };
        }

        if (!abortController.signal.aborted) {
          setNotes(data.items);
          setTotalResults(searchQuery || selectedTag ? data.total : data.items.length);
          setCurrentPage(data.page);
        }
      } catch (err) {
        if (!abortController.signal.aborted) {
          const errorMsg = err instanceof Error ? err.message : 'Failed to load notes';
          setError(errorMsg);
          toast.error(errorMsg);
          console.error('Failed to load notes:', err);
        }
      } finally {
        if (!abortController.signal.aborted) {
          setIsLoading(false);
        }
      }
    };

    loadNotes();

    return () => {
      abortController.abort();
    };
  }, [searchQuery, currentPage, selectedTag]);

  const handleCreateNote = async (noteCreate: { title: string; content: string }) => {
    const tempId = Date.now();
    const tempNote: Note = {
      id: tempId,
      ...noteCreate,
      created_at: new Date().toISOString(),
      tags: [],
    };

    setNotes((prev) => [...prev, tempNote]);

    try {
      const createdNote = await notesApi.create(noteCreate);
      setNotes((prev) =>
        prev.map((note) => (note.id === tempId ? createdNote : note))
      );
    } catch (error) {
      setNotes((prev) => prev.filter((note) => note.id !== tempId));
      throw error;
    }
  };

  const handleUpdateNote = async (id: number, data: NoteUpdate) => {
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
      setNotes(previousNotes);
      throw error;
    }
  };

  const handleDeleteNote = async (id: number) => {
    const previousNotes = [...notes];
    setNotes((prev) => prev.filter((note) => note.id !== id));

    try {
      await notesApi.delete(id);
      if (searchQuery || selectedTag) {
        setCurrentPage(1);
      }
    } catch (error) {
      setNotes(previousNotes);
      throw error;
    }
  };

  /**
   * Handle tag click - toggle tag filter
   * If the same tag is clicked again, clear the filter
   */
  const handleTagClick = (tagName: string) => {
    setSelectedTag((prev) => (prev === tagName ? null : tagName));
    setCurrentPage(1); // Reset to first page when filter changes
  };

  /**
   * Clear the tag filter
   */
  const handleClearTagFilter = () => {
    setSelectedTag(null);
    setCurrentPage(1);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    if (currentPage !== 1) {
      setCurrentPage(1);
    }
  };

  return (
    <section className="notes-section">
      <h2>Notes</h2>
      <NoteForm onSubmit={handleCreateNote} />

      {/* Search Box */}
      <div className="search-box" style={{ margin: '20px 0' }}>
        <input
          type="text"
          value={searchQuery}
          onChange={handleSearchChange}
          placeholder="Search notes by title or content..."
          disabled={!!selectedTag}
          style={{
            width: '100%',
            padding: '10px',
            fontSize: '16px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            opacity: selectedTag ? 0.6 : 1,
          }}
        />
        {searchQuery && !isLoading && (
          <p style={{ marginTop: '10px', color: '#666' }}>
            Found {totalResults} result{totalResults !== 1 ? 's' : ''}
          </p>
        )}
      </div>

      {/* Tag Filter Indicator */}
      {selectedTag && (
        <div
          style={{
            padding: '10px 15px',
            background: '#e3f2fd',
            border: '1px solid #2196f3',
            borderRadius: '4px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}
        >
          <span style={{ fontWeight: 500, color: '#1971c7' }}>
            Filtering by tag: <strong>#{selectedTag}</strong>
          </span>
          <button
            onClick={handleClearTagFilter}
            type="button"
            className="btn-secondary"
            style={{
              padding: '4px 12px',
              fontSize: '14px',
            }}
          >
            Clear filter
          </button>
          <span style={{ color: '#666', fontSize: '14px' }}>
            ({notes.length} note{notes.length !== 1 ? 's' : ''})
          </span>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div
          style={{
            padding: '20px',
            background: '#fee',
            color: '#c33',
            marginBottom: '20px',
          }}
        >
          <p>Error: {error}</p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && notes.length === 0 ? (
        <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
          Loading notes...
        </div>
      ) : notes.length === 0 ? (
        <p>
          {selectedTag
            ? `No notes found with tag "#${selectedTag}"`
            : searchQuery
            ? 'No notes found matching your search.'
            : 'No notes yet. Create one above!'}
        </p>
      ) : (
        <>
          {/* Notes List */}
          <ul className="notes-list">
            {notes.map((note) => (
              <NoteCard
                key={note.id}
                note={note}
                onUpdate={handleUpdateNote}
                onDelete={handleDeleteNote}
                onTagClick={handleTagClick}  // Enable tag filtering!
              />
            ))}
          </ul>

          {/* Pagination (could be enhanced for tag filtering) */}
          {!selectedTag && totalResults > pageSize && (
            <div
              style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                gap: '20px',
                marginTop: '20px',
              }}
            >
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1 || isLoading}
                type="button"
                className="btn-primary"
              >
                Previous
              </button>
              <span>Page {currentPage}</span>
              <button
                onClick={() => setCurrentPage((p) => p + 1)}
                disabled={currentPage * pageSize >= totalResults || isLoading}
                type="button"
                className="btn-primary"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}

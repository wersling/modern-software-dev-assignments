import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { notesApi } from '../../services/api';
import type { Note, NoteUpdate } from '../../types';
import { NoteCard } from './NoteCard';
import { NoteForm } from './NoteForm';
import { TagFilter, TagManager } from '../tags';

export function NotesList() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const pageSize = 10;

  // Tag filtering state
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([]);
  const [filterMode, setFilterMode] = useState<'AND' | 'OR'>('OR');

  useEffect(() => {
    const abortController = new AbortController();

    const loadNotes = async () => {
      setIsLoading(true);
      setError(null);

      try {
        let data;

        // Priority: Tag filter > Search > List all
        if (selectedTagIds.length > 0) {
          // Filter by tags
          // Note: Current backend API only supports single tag_id filter
          // For multi-tag filtering, we'll need to filter client-side
          const response = await notesApi.list();
          const allNotes = response.items;

          let filteredNotes = allNotes.filter((note) => {
            const noteTagIds = note.tags.map((tag) => tag.id);

            if (filterMode === 'AND') {
              // Must have ALL selected tags
              return selectedTagIds.every((tagId) => noteTagIds.includes(tagId));
            } else {
              // OR mode: Must have AT LEAST ONE selected tag
              return selectedTagIds.some((tagId) => noteTagIds.includes(tagId));
            }
          });

          data = {
            items: filteredNotes,
            total: filteredNotes.length,
            page: 1,
            page_size: pageSize,
            total_pages: Math.ceil(filteredNotes.length / pageSize),
          };
        } else if (searchQuery) {
          // Search mode
          data = await notesApi.search(searchQuery, currentPage, pageSize);
        } else {
          // List all mode
          data = await notesApi.list();
        }

        if (!abortController.signal.aborted) {
          setNotes(data.items);
          setTotalResults(searchQuery || selectedTagIds.length > 0 ? data.total : data.items.length);
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

    const debounceTimeout = setTimeout(() => {
      loadNotes();
    }, searchQuery && selectedTagIds.length === 0 ? 300 : 0);

    return () => {
      clearTimeout(debounceTimeout);
      abortController.abort();
    };
  }, [searchQuery, currentPage, selectedTagIds, filterMode]);

  const handleCreateNote = async (noteCreate: { title: string; content: string }) => {
    const tempId = Date.now();
    const tempNote: Note = {
      id: tempId,
      ...noteCreate,
      created_at: new Date().toISOString(),
      tags: [], // Initialize with empty tags array
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
      if (searchQuery) {
        setCurrentPage(1);
      }
    } catch (error) {
      setNotes(previousNotes);
      throw error;
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    // Clear tag filters when searching
    if (e.target.value && selectedTagIds.length > 0) {
      setSelectedTagIds([]);
    }
    if (currentPage !== 1) {
      setCurrentPage(1);
    }
  };

  const handleTagToggle = (tagId: number) => {
    setSelectedTagIds((prev) => {
      const isSelected = prev.includes(tagId);
      const newSelected = isSelected
        ? prev.filter((id) => id !== tagId)
        : [...prev, tagId];

      // Clear search when filtering by tags
      if (newSelected.length > 0 && searchQuery) {
        setSearchQuery('');
      }

      return newSelected;
    });
    setCurrentPage(1);
  };

  const handleClearFilters = () => {
    setSelectedTagIds([]);
    setCurrentPage(1);
  };

  const handleRetry = () => {
    setSearchQuery((prev) => prev);
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    const maxPage = Math.ceil(totalResults / pageSize);
    if (currentPage < maxPage) {
      setCurrentPage(currentPage + 1);
    }
  };

  const totalPages = Math.ceil(totalResults / pageSize);
  const showPagination = totalResults > pageSize;

  return (
    <section className="notes-section">
      <h2>Notes</h2>
      <NoteForm onSubmit={handleCreateNote} />

      {/* Tag Filter */}
      <TagFilter
        selectedTagIds={selectedTagIds}
        onTagToggle={handleTagToggle}
        onClearFilters={handleClearFilters}
        disabled={isLoading}
        filterMode={filterMode}
        onFilterModeChange={setFilterMode}
      />

      {/* Tag Manager */}
      <TagManager
        onTagCreated={() => {
          // Refresh notes when a new tag is created
          setSearchQuery((prev) => prev);
        }}
        onTagDeleted={() => {
          // Refresh notes when a tag is deleted
          setSearchQuery((prev) => prev);
        }}
      />

      {/* Search Box */}
      <div className="search-box" style={{ margin: '20px 0' }}>
        <input
          type="text"
          value={searchQuery}
          onChange={handleSearchChange}
          placeholder="Search notes by title or content..."
          disabled={selectedTagIds.length > 0}
          style={{
            width: '100%',
            padding: '10px',
            fontSize: '16px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            opacity: selectedTagIds.length > 0 ? 0.6 : 1,
          }}
        />
        {searchQuery && !isLoading && (
          <p style={{ marginTop: '10px', color: '#666' }}>
            Found {totalResults} result{totalResults !== 1 ? 's' : ''}
          </p>
        )}
        {searchQuery && isLoading && (
          <p style={{ marginTop: '10px', color: '#999' }}>
            Searching...
          </p>
        )}
        {selectedTagIds.length > 0 && !searchQuery && (
          <p style={{ marginTop: '10px', color: '#666', fontSize: '0.9rem' }}>
            💡 Search is disabled while tag filters are active. Clear filters to search.
          </p>
        )}
      </div>

      {error && (
        <div style={{ padding: '20px', background: '#fee', color: '#c33', marginBottom: '20px' }}>
          <p>Error: {error}</p>
          <button onClick={handleRetry} type="button" className="btn-primary">
            Retry
          </button>
        </div>
      )}

      {isLoading && notes.length === 0 ? (
        <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
          Loading notes...
        </div>
      ) : notes.length === 0 ? (
        <p>
          {searchQuery
            ? 'No notes found matching your search.'
            : selectedTagIds.length > 0
            ? 'No notes found with the selected tags.'
            : 'No notes yet. Create one above!'}
        </p>
      ) : (
        <>
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

          {showPagination && (
            <div
              className="pagination-controls"
              style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                gap: '20px',
                marginTop: '20px',
              }}
            >
              <button
                onClick={handlePreviousPage}
                disabled={currentPage === 1 || isLoading}
                type="button"
                className="btn-primary"
                style={{ opacity: currentPage === 1 || isLoading ? 0.5 : 1 }}
              >
                Previous
              </button>
              <span>
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={handleNextPage}
                disabled={currentPage >= totalPages || isLoading}
                type="button"
                className="btn-primary"
                style={{ opacity: currentPage >= totalPages || isLoading ? 0.5 : 1 }}
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

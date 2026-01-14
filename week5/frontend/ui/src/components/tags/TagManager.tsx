import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { tagsApi } from '../../services/tagsApi';
import type { Tag } from '../../types';

export interface TagManagerProps {
  onTagCreated?: (tag: Tag) => void;
  onTagDeleted?: (tagId: number) => void;
  showStats?: boolean;
}

/**
 * TagManager Component
 *
 * Provides functionality to create, view, and delete tags.
 * Shows statistics about tag usage if enabled.
 */
export function TagManager({ onTagCreated, onTagDeleted }: TagManagerProps) {
  const [tags, setTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [newTagName, setNewTagName] = useState('');
  const [deletingTagIds, setDeletingTagIds] = useState<Set<number>>(new Set());
  const [isExpanded, setIsExpanded] = useState(false);

  // Load all tags on component mount or when expanded
  useEffect(() => {
    if (!isExpanded) return;

    const abortController = new AbortController();

    const loadTags = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const allTags = await tagsApi.list();

        if (!abortController.signal.aborted) {
          setTags(allTags);
        }
      } catch (err) {
        if (!abortController.signal.aborted) {
          const errorMsg = err instanceof Error ? err.message : 'Failed to load tags';
          setError(errorMsg);
          console.error('Failed to load tags:', err);
        }
      } finally {
        if (!abortController.signal.aborted) {
          setIsLoading(false);
        }
      }
    };

    loadTags();

    return () => {
      abortController.abort();
    };
  }, [isExpanded]);

  const handleCreateTag = async (e: React.FormEvent) => {
    e.preventDefault();

    const trimmedName = newTagName.trim();

    if (!trimmedName) {
      toast.error('Tag name is required');
      return;
    }

    // Check if tag already exists (case-insensitive)
    const tagExists = tags.some(
      (tag) => tag.name.toLowerCase() === trimmedName.toLowerCase()
    );

    if (tagExists) {
      toast.error('Tag already exists');
      return;
    }

    // Validate tag name format (no spaces, starts with letter/number)
    if (/\s/.test(trimmedName)) {
      toast.error('Tag name cannot contain spaces');
      return;
    }

    if (!/^[a-zA-Z0-9]/.test(trimmedName)) {
      toast.error('Tag name must start with a letter or number');
      return;
    }

    setIsCreating(true);

    try {
      const createdTag = await tagsApi.create(trimmedName);
      setTags((prev) => [...prev, createdTag]);
      setNewTagName('');
      toast.success(`Tag "${createdTag.name}" created successfully`);
      onTagCreated?.(createdTag);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to create tag';
      toast.error(errorMsg);
      console.error('Failed to create tag:', err);
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteTag = async (tagId: number, tagName: string) => {
    if (!window.confirm(`Are you sure you want to delete tag "${tagName}"?`)) {
      return;
    }

    setDeletingTagIds((prev) => new Set(prev).add(tagId));

    try {
      await tagsApi.delete(tagId);
      setTags((prev) => prev.filter((tag) => tag.id !== tagId));
      toast.success(`Tag "${tagName}" deleted successfully`);
      onTagDeleted?.(tagId);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to delete tag';
      toast.error(errorMsg);
      console.error('Failed to delete tag:', err);
    } finally {
      setDeletingTagIds((prev) => {
        const newSet = new Set(prev);
        newSet.delete(tagId);
        return newSet;
      });
    }
  };

  // Generate color for each tag
  const getTagColor = (name: string): string => {
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }

    const hue = Math.abs(hash % 360);
    const saturation = 60 + (Math.abs(hash >> 8) % 20);
    const lightness = 85 + (Math.abs(hash >> 16) % 10);

    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  };

  return (
    <div
      className="tag-manager"
      style={{
        padding: '15px',
        background: '#fff',
        border: '1px solid #dee2e6',
        borderRadius: '4px',
        marginTop: '15px',
      }}
    >
      {/* Toggle button */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="btn-toggle-manager"
        style={{
          width: '100%',
          padding: '10px 15px',
          border: '1px solid #dee2e6',
          borderRadius: '4px',
          background: '#f8f9fa',
          color: '#495057',
          cursor: 'pointer',
          fontSize: '1rem',
          fontWeight: 600,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          transition: 'all 0.2s ease',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = '#e9ecef';
          e.currentTarget.style.borderColor = '#adb5bd';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = '#f8f9fa';
          e.currentTarget.style.borderColor = '#dee2e6';
        }}
      >
        <span>🏷️ Manage Tags</span>
        <span style={{ fontSize: '1.2rem' }}>{isExpanded ? '▼' : '▶'}</span>
      </button>

      {/* Expanded content */}
      {isExpanded && (
        <div style={{ marginTop: '15px' }}>
          {/* Create tag form */}
          <form
            onSubmit={handleCreateTag}
            className="tag-create-form"
            style={{
              display: 'flex',
              gap: '10px',
              marginBottom: '15px',
              flexWrap: 'wrap',
            }}
          >
            <input
              type="text"
              value={newTagName}
              onChange={(e) => setNewTagName(e.target.value)}
              placeholder="New tag name (e.g., work, urgent)"
              disabled={isCreating}
              style={{
                flex: 1,
                minWidth: '200px',
                padding: '8px 12px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                fontSize: '0.95rem',
                opacity: isCreating ? 0.6 : 1,
              }}
              aria-label="New tag name"
            />
            <button
              type="submit"
              disabled={isCreating || !newTagName.trim()}
              className="btn-primary"
              style={{
                padding: '8px 16px',
                border: '1px solid #28a745',
                borderRadius: '4px',
                background: '#28a745',
                color: '#fff',
                cursor: isCreating || !newTagName.trim() ? 'not-allowed' : 'pointer',
                fontSize: '0.95rem',
                fontWeight: 500,
                opacity: isCreating || !newTagName.trim() ? 0.6 : 1,
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                if (!isCreating && newTagName.trim()) {
                  e.currentTarget.style.background = '#218838';
                  e.currentTarget.style.borderColor = '#1e7e34';
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#28a745';
                e.currentTarget.style.borderColor = '#28a745';
              }}
            >
              {isCreating ? 'Creating...' : 'Create Tag'}
            </button>
          </form>

          {/* Error state */}
          {error && (
            <div
              style={{
                padding: '10px',
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '4px',
                color: '#721c24',
                marginBottom: '15px',
                fontSize: '0.9rem',
              }}
            >
              Error: {error}
            </div>
          )}

          {/* Loading state */}
          {isLoading && tags.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px', color: '#6c757d' }}>
              Loading tags...
            </div>
          ) : tags.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px', color: '#6c757d', fontStyle: 'italic' }}>
              No tags yet. Create your first tag above!
            </div>
          ) : (
            <>
              {/* Tags list */}
              <div className="tags-list-manager">
                <h4
                  style={{
                    margin: '0 0 10px 0',
                    fontSize: '0.95rem',
                    fontWeight: 600,
                    color: '#495057',
                  }}
                >
                  All Tags ({tags.length})
                </h4>
                <div
                  style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '10px',
                  }}
                >
                  {tags.map((tag) => {
                    const isDeleting = deletingTagIds.has(tag.id);
                    const backgroundColor = getTagColor(tag.name);

                    return (
                      <div
                        key={tag.id}
                        className="tag-manager-item"
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '6px 12px',
                          background: backgroundColor,
                          borderRadius: '16px',
                          border: '1px solid #dee2e6',
                        }}
                      >
                        <span
                          style={{
                            fontSize: '0.9rem',
                            fontWeight: 500,
                            color: '#333',
                          }}
                        >
                          #{tag.name}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleDeleteTag(tag.id, tag.name)}
                          disabled={isDeleting}
                          className="btn-delete-tag"
                          style={{
                            padding: '2px 6px',
                            border: 'none',
                            borderRadius: '3px',
                            background: 'transparent',
                            color: '#dc3545',
                            cursor: isDeleting ? 'not-allowed' : 'pointer',
                            fontSize: '1rem',
                            opacity: isDeleting ? 0.6 : 1,
                            transition: 'all 0.2s ease',
                          }}
                          onMouseEnter={(e) => {
                            if (!isDeleting) {
                              e.currentTarget.style.background = '#dc3545';
                              e.currentTarget.style.color = '#fff';
                            }
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'transparent';
                            e.currentTarget.style.color = '#dc3545';
                          }}
                          title={`Delete tag: ${tag.name}`}
                          aria-label={`Delete tag: ${tag.name}`}
                        >
                          {isDeleting ? '...' : '✕'}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Instructions */}
              <div
                style={{
                  marginTop: '15px',
                  padding: '10px',
                  background: '#f8f9fa',
                  borderRadius: '4px',
                  fontSize: '0.85rem',
                  color: '#6c757d',
                }}
              >
                <p style={{ margin: '0 0 5px 0', fontWeight: 500 }}>
                  💡 Tag Management Tips:
                </p>
                <ul style={{ margin: 0, paddingLeft: '20px' }}>
                  <li>Tag names must start with a letter or number</li>
                  <li>Tag names cannot contain spaces</li>
                  <li>Deleting a tag removes it from all notes</li>
                </ul>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { tagsApi } from '../../services/tagsApi';
import type { Tag } from '../../types';

export interface TagFilterProps {
  selectedTagIds: number[];
  onTagToggle: (tagId: number) => void;
  onClearFilters: () => void;
  disabled?: boolean;
  filterMode?: 'AND' | 'OR';
  onFilterModeChange?: (mode: 'AND' | 'OR') => void;
}

/**
 * TagFilter Component
 *
 * Displays a list of all available tags with filtering capabilities.
 * Supports multi-select filtering with AND/OR logic modes.
 */
export function TagFilter({
  selectedTagIds,
  onTagToggle,
  onClearFilters,
  disabled = false,
  filterMode = 'OR',
  onFilterModeChange,
}: TagFilterProps) {
  const [tags, setTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load all tags on component mount
  useEffect(() => {
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
  }, []);

  const handleTagClick = (tagId: number) => {
    if (!disabled) {
      onTagToggle(tagId);
    }
  };

  const handleClearFilters = () => {
    if (!disabled) {
      onClearFilters();
      toast.info('Tag filters cleared');
    }
  };

  const handleFilterModeChange = (mode: 'AND' | 'OR') => {
    if (!disabled && onFilterModeChange) {
      onFilterModeChange(mode);
    }
  };

  // Generate color for each tag (same logic as NoteCard)
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

  // Show loading state
  if (isLoading) {
    return (
      <div className="tag-filter" style={{ padding: '15px', background: '#f8f9fa', borderRadius: '4px', marginBottom: '15px' }}>
        <div style={{ textAlign: 'center', color: '#6c757d', fontSize: '0.9rem' }}>
          Loading tags...
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="tag-filter" style={{ padding: '15px', background: '#f8d7da', borderRadius: '4px', marginBottom: '15px' }}>
        <p style={{ margin: 0, color: '#721c24', fontSize: '0.9rem' }}>
          Error loading tags: {error}
        </p>
      </div>
    );
  }

  // No tags available
  if (tags.length === 0) {
    return (
      <div className="tag-filter" style={{ padding: '15px', background: '#f8f9fa', borderRadius: '4px', marginBottom: '15px' }}>
        <p style={{ margin: 0, color: '#6c757d', fontSize: '0.9rem', textAlign: 'center' }}>
          No tags available yet
        </p>
      </div>
    );
  }

  const hasActiveFilters = selectedTagIds.length > 0;

  return (
    <div className="tag-filter" style={{ padding: '15px', background: '#f8f9fa', borderRadius: '4px', marginBottom: '15px' }}>
      {/* Header with title and clear button */}
      <div
        className="tag-filter-header"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '12px',
          flexWrap: 'wrap',
          gap: '10px',
        }}
      >
        <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: '#333' }}>
          Filter by Tags
        </h3>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {/* Filter mode selector (if provided) */}
          {onFilterModeChange && (
            <div
              className="filter-mode-selector"
              style={{ display: 'flex', gap: '5px', background: '#fff', padding: '4px', borderRadius: '4px', border: '1px solid #dee2e6' }}
            >
              <button
                type="button"
                onClick={() => handleFilterModeChange('OR')}
                disabled={disabled}
                className={`filter-mode-btn ${filterMode === 'OR' ? 'active' : ''}`}
                style={{
                  padding: '4px 12px',
                  border: 'none',
                  borderRadius: '3px',
                  background: filterMode === 'OR' ? '#007bff' : 'transparent',
                  color: filterMode === 'OR' ? '#fff' : '#495057',
                  cursor: disabled ? 'not-allowed' : 'pointer',
                  fontSize: '0.85rem',
                  fontWeight: 500,
                  opacity: disabled ? 0.6 : 1,
                }}
                title="Match any selected tag"
              >
                OR
              </button>
              <button
                type="button"
                onClick={() => handleFilterModeChange('AND')}
                disabled={disabled}
                className={`filter-mode-btn ${filterMode === 'AND' ? 'active' : ''}`}
                style={{
                  padding: '4px 12px',
                  border: 'none',
                  borderRadius: '3px',
                  background: filterMode === 'AND' ? '#007bff' : 'transparent',
                  color: filterMode === 'AND' ? '#fff' : '#495057',
                  cursor: disabled ? 'not-allowed' : 'pointer',
                  fontSize: '0.85rem',
                  fontWeight: 500,
                  opacity: disabled ? 0.6 : 1,
                }}
                title="Match all selected tags"
              >
                AND
              </button>
            </div>
          )}

          {/* Clear filters button */}
          {hasActiveFilters && (
            <button
              type="button"
              onClick={handleClearFilters}
              disabled={disabled}
              className="btn-clear-filters"
              style={{
                padding: '6px 12px',
                border: '1px solid #dc3545',
                borderRadius: '4px',
                background: '#dc3545',
                color: '#fff',
                cursor: disabled ? 'not-allowed' : 'pointer',
                fontSize: '0.85rem',
                fontWeight: 500,
                opacity: disabled ? 0.6 : 1,
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                if (!disabled) {
                  e.currentTarget.style.background = '#c82333';
                  e.currentTarget.style.borderColor = '#bd2130';
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#dc3545';
                e.currentTarget.style.borderColor = '#dc3545';
              }}
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Active filters indicator */}
      {hasActiveFilters && (
        <div
          className="active-filters-indicator"
          style={{
            padding: '8px 12px',
            background: '#e7f3ff',
            border: '1px solid #b3d7ff',
            borderRadius: '4px',
            marginBottom: '12px',
            fontSize: '0.85rem',
            color: '#004085',
          }}
        >
          <strong>Filtering by:</strong>{' '}
          {tags
            .filter((tag) => selectedTagIds.includes(tag.id))
            .map((tag) => tag.name)
            .join(', ')}
          {filterMode === 'AND' && ' (all tags required)'}
          {filterMode === 'OR' && ' (any tag)'}
        </div>
      )}

      {/* Tags list */}
      <div
        className="tags-list"
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '8px',
        }}
      >
        {tags.map((tag) => {
          const isSelected = selectedTagIds.includes(tag.id);
          const backgroundColor = getTagColor(tag.name);

          return (
            <button
              key={tag.id}
              type="button"
              onClick={() => handleTagClick(tag.id)}
              disabled={disabled}
              className={`tag-filter-chip ${isSelected ? 'selected' : ''}`}
              style={{
                padding: '6px 14px',
                border: '2px solid',
                borderColor: isSelected ? '#007bff' : backgroundColor,
                borderRadius: '16px',
                background: isSelected ? '#e7f3ff' : backgroundColor,
                color: '#333',
                cursor: disabled ? 'not-allowed' : 'pointer',
                fontSize: '0.9rem',
                fontWeight: isSelected ? 600 : 500,
                transition: 'all 0.2s ease',
                opacity: disabled ? 0.6 : 1,
                userSelect: 'none',
              }}
              onMouseEnter={(e) => {
                if (!disabled && !isSelected) {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.15)';
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
              title={isSelected ? `Remove filter: ${tag.name}` : `Add filter: ${tag.name}`}
              aria-pressed={isSelected}
              aria-label={`Filter by tag: ${tag.name}${isSelected ? ' (selected)' : ''}`}
            >
              #{tag.name}
            </button>
          );
        })}
      </div>

      {/* Instructions */}
      {tags.length > 0 && !hasActiveFilters && (
        <p
          style={{
            marginTop: '12px',
            marginBottom: 0,
            fontSize: '0.85rem',
            color: '#6c757d',
            fontStyle: 'italic',
          }}
        >
          Click on tags to filter notes
        </p>
      )}
    </div>
  );
}

import { useState } from 'react';
import { toast } from 'react-toastify';
import type { Note, NoteUpdate } from '../../types';

interface NoteCardProps {
  note: Note;
  onUpdate: (id: number, data: NoteUpdate) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
  onTagClick?: (tagName: string) => void; // Optional callback for tag filtering
}

/**
 * Generate a consistent color based on tag name using simple hash
 * @param name - Tag name to generate color for
 * @returns HSL color string
 */
function getTagColor(name: string): string {
  // Simple hash function to generate a number from string
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }

  // Use hash to generate hue (0-360), saturation (60-80%), lightness (85-95%)
  const hue = Math.abs(hash % 360);
  const saturation = 60 + (Math.abs(hash >> 8) % 20); // 60-80%
  const lightness = 85 + (Math.abs(hash >> 16) % 10); // 85-95%

  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

export function NoteCard({ note, onUpdate, onDelete, onTagClick }: NoteCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [editTitle, setEditTitle] = useState(note.title);
  const [editContent, setEditContent] = useState(note.content);

  const formatDate = new Date(note.created_at).toLocaleString();

  const handleEdit = () => {
    setIsEditing(true);
    setEditTitle(note.title);
    setEditContent(note.content);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditTitle(note.title);
    setEditContent(note.content);
  };

  const handleSave = async () => {
    if (!editTitle.trim() || !editContent.trim()) {
      toast.error('Title and content are required');
      return;
    }

    setIsSaving(true);
    try {
      await onUpdate(note.id, { title: editTitle, content: editContent });
      setIsEditing(false);
      toast.success('Note updated successfully');
    } catch (error) {
      console.error('Failed to update note:', error);
      const errorMsg = error instanceof Error ? error.message : 'Failed to update note';
      toast.error(errorMsg);
      // Reset to original values
      setEditTitle(note.title);
      setEditContent(note.content);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      setIsDeleting(true);
      try {
        await onDelete(note.id);
        toast.success('Note deleted successfully');
      } catch (error) {
        console.error('Failed to delete note:', error);
        const errorMsg = error instanceof Error ? error.message : 'Failed to delete note';
        toast.error(errorMsg);
        setIsDeleting(false);
      }
    }
  };

  if (isEditing) {
    return (
      <li className="note-card editing">
        <article>
          <div className="note-form">
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              placeholder="Note title"
              className="note-input"
              disabled={isSaving}
              aria-label="Note title"
            />
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              placeholder="Note content"
              className="note-textarea"
              disabled={isSaving}
              rows={4}
              aria-label="Note content"
            />
            <div className="note-actions">
              <button
                type="button"
                onClick={handleSave}
                disabled={isSaving || !editTitle.trim() || !editContent.trim()}
                className="btn-primary"
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                disabled={isSaving}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </article>
      </li>
    );
  }

  // Render tags if they exist
  const renderTags = () => {
    if (!note.tags || note.tags.length === 0) {
      return null;
    }

    return (
      <div className="note-tags">
        {note.tags.map((tag) => {
          const backgroundColor = getTagColor(tag.name);
          return (
            <span
              key={tag.id}
              className="tag-chip"
              style={{ backgroundColor }}
              onClick={() => onTagClick?.(tag.name)}
              title={onTagClick ? `Filter by tag: ${tag.name}` : tag.name}
              aria-label={`Tag: ${tag.name}`}
            >
              #{tag.name}
            </span>
          );
        })}
      </div>
    );
  };

  return (
    <li className="note-card">
      <article>
        <div className="note-header">
          <h3>{note.title}</h3>
          <div className="note-actions">
            <button
              type="button"
              onClick={handleEdit}
              disabled={isDeleting}
              className="btn-icon"
              aria-label="Edit note"
              title="Edit note"
            >
              ✏️
            </button>
            <button
              type="button"
              onClick={handleDelete}
              disabled={isDeleting}
              className="btn-icon btn-danger"
              aria-label="Delete note"
              title="Delete note"
            >
              {isDeleting ? '...' : '🗑️'}
            </button>
          </div>
        </div>
        <p>{note.content}</p>
        {/* Display tags between content and timestamp */}
        {renderTags()}
        <time dateTime={note.created_at}>{formatDate}</time>
      </article>
    </li>
  );
}

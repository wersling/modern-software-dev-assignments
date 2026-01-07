import { useState } from 'react';
import type { FormEvent } from 'react';
import { toast } from 'react-toastify';
import type { NoteCreate } from '../../types';

interface NoteFormProps {
  onSubmit: (note: NoteCreate) => Promise<void>;
}

export function NoteForm({ onSubmit }: NoteFormProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      toast.error('Title and content are required');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({ title: title.trim(), content: content.trim() });
      setTitle('');
      setContent('');
    } catch (error) {
      console.error('Failed to create note:', error);
      const errorMsg = error instanceof Error ? error.message : 'Failed to create note. Please try again.';
      toast.error(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="note-form">
      <input
        type="text"
        placeholder="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
        disabled={isSubmitting}
      />
      <input
        type="text"
        placeholder="Content"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        required
        disabled={isSubmitting}
      />
      <button type="submit" disabled={isSubmitting || !title.trim() || !content.trim()}>
        {isSubmitting ? 'Adding...' : 'Add'}
      </button>
    </form>
  );
}

import { useState } from 'react';
import type { FormEvent } from 'react';
import type { ActionItemCreate } from '../../types';

interface ActionItemFormProps {
  onSubmit: (item: ActionItemCreate) => Promise<void>;
}

export function ActionItemForm({ onSubmit }: ActionItemFormProps) {
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!description.trim()) return;

    setIsSubmitting(true);
    try {
      await onSubmit({ description: description.trim() });
      setDescription('');
    } catch (error) {
      console.error('Failed to create action item:', error);
      alert('Failed to create action item. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="action-item-form">
      <input
        type="text"
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
        disabled={isSubmitting}
      />
      <button type="submit" disabled={isSubmitting || !description.trim()}>
        {isSubmitting ? 'Adding...' : 'Add'}
      </button>
    </form>
  );
}

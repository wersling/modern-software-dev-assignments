import { useState } from 'react';
import type { ActionItem } from '../../types';

interface ActionItemCardProps {
  item: ActionItem;
  onComplete: (id: number) => Promise<void>;
}

export function ActionItemCard({ item, onComplete }: ActionItemCardProps) {
  const [isCompleting, setIsCompleting] = useState(false);

  const handleComplete = async () => {
    if (isCompleting) return;

    setIsCompleting(true);
    try {
      await onComplete(item.id);
    } catch (error) {
      console.error('Failed to complete action item:', error);
      alert('Failed to complete action item. Please try again.');
      setIsCompleting(false);
    }
    // Note: We don't reset isCompleting here because the parent component
    // will re-render with the updated data
  };

  const formatDate = new Date(item.created_at).toLocaleString();

  return (
    <li className={`action-item-card ${item.completed ? 'completed' : ''}`}>
      <article>
        <span className={`status ${item.completed ? 'done' : 'open'}`}>
          [{item.completed ? 'done' : 'open'}]
        </span>
        <span className="description">{item.description}</span>
        <time dateTime={item.created_at}>{formatDate}</time>
        {!item.completed && (
          <button
            type="button"
            onClick={handleComplete}
            disabled={isCompleting}
            className="complete-btn"
          >
            {isCompleting ? 'Completing...' : 'Complete'}
          </button>
        )}
      </article>
    </li>
  );
}

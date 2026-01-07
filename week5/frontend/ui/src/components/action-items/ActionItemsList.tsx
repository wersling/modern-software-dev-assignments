import { useEffect, useState } from 'react';
import { actionItemsApi } from '../../services/api';
import type { ActionItem } from '../../types';
import { ActionItemCard } from './ActionItemCard';
import { ActionItemForm } from './ActionItemForm';

export function ActionItemsList() {
  const [items, setItems] = useState<ActionItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadItems = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await actionItemsApi.list();
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load action items');
      console.error('Failed to load action items:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, []);

  const handleCreateItem = async (itemCreate: { description: string }) => {
    // Optimistic update - immediately add the item to the list
    const tempId = Date.now();
    const tempItem: ActionItem = {
      id: tempId,
      ...itemCreate,
      completed: false,
      created_at: new Date().toISOString(),
    };

    setItems((prev) => [...prev, tempItem]);

    try {
      const createdItem = await actionItemsApi.create(itemCreate);
      // Replace the temporary item with the real one from the server
      setItems((prev) =>
        prev.map((item) => (item.id === tempId ? createdItem : item))
      );
    } catch (error) {
      // Rollback on error
      setItems((prev) => prev.filter((item) => item.id !== tempId));
      throw error;
    }
  };

  const handleCompleteItem = async (id: number) => {
    // Optimistic update - immediately mark as completed
    setItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, completed: true } : item
      )
    );

    try {
      await actionItemsApi.complete(id);
      // No need to update state further, the optimistic update is correct
    } catch (error) {
      // Rollback on error - reload the list
      console.error('Failed to complete item, reloading:', error);
      await loadItems();
      throw error;
    }
  };

  if (isLoading) {
    return <div>Loading action items...</div>;
  }

  if (error) {
    return (
      <div>
        <p>Error: {error}</p>
        <button onClick={loadItems} type="button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <section className="action-items-section">
      <h2>Action Items</h2>
      <ActionItemForm onSubmit={handleCreateItem} />
      {items.length === 0 ? (
        <p>No action items yet. Create one above!</p>
      ) : (
        <ul className="action-items-list">
          {items.map((item) => (
            <ActionItemCard
              key={item.id}
              item={item}
              onComplete={handleCompleteItem}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

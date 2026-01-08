import { useCallback, useEffect, useMemo, useState } from 'react';
import { actionItemsApi } from '../../services/api';
import type { ActionItem } from '../../types';
import { ActionItemCard } from './ActionItemCard';
import { ActionItemForm } from './ActionItemForm';

type FilterType = 'all' | 'active' | 'completed';

export function ActionItemsList() {
  const [items, setItems] = useState<ActionItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterType>('all');
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [isBulkCompleting, setIsBulkCompleting] = useState(false);

  // Use useCallback to memoize loadItems and prevent unnecessary re-renders
  const loadItems = useCallback(async (completed?: boolean) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await actionItemsApi.list(completed);
      setItems(data);
      // Clear selection when loading new data
      setSelectedIds(new Set());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load action items');
      console.error('Failed to load action items:', err);
    } finally {
      setIsLoading(false);
    }
  }, []); // No dependencies - all functions used are stable

  useEffect(() => {
    // Convert filter to API parameter
    const completedParam = filter === 'active' ? false : filter === 'completed' ? true : undefined;
    loadItems(completedParam);
  }, [filter, loadItems]); // Add loadItems to dependencies

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
      const completedParam = filter === 'active' ? false : filter === 'completed' ? true : undefined;
      await loadItems(completedParam);
      throw error;
    }
  };

  const handleToggleSelect = (id: number) => {
    setSelectedIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const handleBulkComplete = async () => {
    if (selectedIds.size === 0 || isBulkCompleting) return;

    const idsArray = Array.from(selectedIds);
    const previouslyCompletedItems = items.filter(item =>
      idsArray.includes(item.id) && item.completed
    );

    // Skip if all selected items are already completed
    if (previouslyCompletedItems.length === idsArray.length) {
      return;
    }

    // Optimistic update - immediately mark all selected items as completed
    setItems((prev) =>
      prev.map((item) =>
        selectedIds.has(item.id) ? { ...item, completed: true } : item
      )
    );

    setIsBulkCompleting(true);
    try {
      const result = await actionItemsApi.bulkComplete({ ids: idsArray });

      // Log success
      console.log(`Successfully completed ${result.total_updated} action item(s)`);
      if (result.not_found.length > 0) {
        console.warn(`Some items were not found: ${result.not_found.join(', ')}`);
      }

      // Reload to ensure sync with server
      const completedParam = filter === 'active' ? false : filter === 'completed' ? true : undefined;
      await loadItems(completedParam);

      // Clear selection after successful bulk complete
      setSelectedIds(new Set());
    } catch (error) {
      // Rollback on error - reload the list
      console.error('Failed to bulk complete items, reloading:', error);
      const completedParam = filter === 'active' ? false : filter === 'completed' ? true : undefined;
      await loadItems(completedParam);
      alert('Failed to complete some items. Please try again.');
    } finally {
      setIsBulkCompleting(false);
    }
  };

  // Memoize computed values for performance
  const activeItemsCount = useMemo(
    () => items.filter(item => !item.completed).length,
    [items]
  );

  const completedItemsCount = useMemo(
    () => items.filter(item => item.completed).length,
    [items]
  );

  const selectedActiveCount = useMemo(
    () => Array.from(selectedIds).filter(
      id => items.find(item => item.id === id && !item.completed)
    ).length,
    [selectedIds, items]
  );

  if (isLoading) {
    return <div className="loading">Loading action items...</div>;
  }

  if (error) {
    return (
      <div className="error">
        <p>Error: {error}</p>
        <button onClick={() => loadItems()} type="button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <section className="action-items-section">
      <h2>Action Items</h2>
      <ActionItemForm onSubmit={handleCreateItem} />

      {/* Filter Controls */}
      <div className="action-items-controls">
        <div className="filter-buttons">
          <button
            type="button"
            onClick={() => setFilter('all')}
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            aria-label="Show all action items"
          >
            All ({items.length})
          </button>
          <button
            type="button"
            onClick={() => setFilter('active')}
            className={`filter-btn ${filter === 'active' ? 'active' : ''}`}
            aria-label="Show active action items"
          >
            Active ({activeItemsCount})
          </button>
          <button
            type="button"
            onClick={() => setFilter('completed')}
            className={`filter-btn ${filter === 'completed' ? 'active' : ''}`}
            aria-label="Show completed action items"
          >
            Completed ({completedItemsCount})
          </button>
        </div>

        {/* Bulk Complete Button */}
        {filter !== 'completed' && selectedActiveCount > 0 && (
          <div className="bulk-actions">
            <span className="selected-count">{selectedActiveCount} selected</span>
            <button
              type="button"
              onClick={handleBulkComplete}
              disabled={isBulkCompleting}
              className="bulk-complete-btn"
            >
              {isBulkCompleting ? 'Completing...' : `Complete ${selectedActiveCount} Item${selectedActiveCount > 1 ? 's' : ''}`}
            </button>
          </div>
        )}
      </div>

      {items.length === 0 ? (
        <p className="empty-state">No action items found. Create one above!</p>
      ) : (
        <ul className="action-items-list">
          {items.map((item) => (
            <ActionItemCard
              key={item.id}
              item={item}
              onComplete={handleCompleteItem}
              isSelected={selectedIds.has(item.id)}
              onToggleSelect={handleToggleSelect}
              showCheckbox={filter !== 'completed'}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

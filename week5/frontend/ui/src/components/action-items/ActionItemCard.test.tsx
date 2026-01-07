import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ActionItemCard } from './ActionItemCard';
import type { ActionItem } from '../../types';

describe('ActionItemCard', () => {
  const mockItem: ActionItem = {
    id: 1,
    description: 'Test action item',
    completed: false,
    created_at: '2024-01-01T00:00:00Z',
  };

  it('renders action item details', () => {
    const mockOnComplete = vi.fn();
    render(<ActionItemCard item={mockItem} onComplete={mockOnComplete} />);

    expect(screen.getByText('[open]')).toBeInTheDocument();
    expect(screen.getByText('Test action item')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Complete' })).toBeInTheDocument();
  });

  it('shows completed status when item is completed', () => {
    const completedItem: ActionItem = { ...mockItem, completed: true };
    const mockOnComplete = vi.fn();
    render(<ActionItemCard item={completedItem} onComplete={mockOnComplete} />);

    expect(screen.getByText('[done]')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Complete' })).not.toBeInTheDocument();
  });

  it('calls onComplete when complete button is clicked', async () => {
    const mockOnComplete = vi.fn().mockResolvedValue(undefined);
    render(<ActionItemCard item={mockItem} onComplete={mockOnComplete} />);

    const completeButton = screen.getByRole('button', { name: 'Complete' });
    fireEvent.click(completeButton);

    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalledWith(1);
    });
  });

  it('disables button while completing', async () => {
    let resolveComplete: (value: void) => void;
    const mockOnComplete = vi.fn().mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveComplete = resolve;
        })
    );
    render(<ActionItemCard item={mockItem} onComplete={mockOnComplete} />);

    const completeButton = screen.getByRole('button', { name: 'Complete' });
    fireEvent.click(completeButton);

    // Button should be disabled
    expect(completeButton).toBeDisabled();
    expect(screen.getByText('Completing...')).toBeInTheDocument();

    // Resolve the promise
    resolveComplete!();

    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalled();
    });
  });

  it('prevents multiple clicks while completing', async () => {
    let resolveComplete: (value: void) => void;
    const mockOnComplete = vi.fn().mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveComplete = resolve;
        })
    );
    render(<ActionItemCard item={mockItem} onComplete={mockOnComplete} />);

    const completeButton = screen.getByRole('button', { name: 'Complete' });

    // Click multiple times
    fireEvent.click(completeButton);
    fireEvent.click(completeButton);
    fireEvent.click(completeButton);

    // Should only call once
    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalledTimes(1);
    });

    resolveComplete!();
  });

  it('displays formatted creation date', () => {
    const mockOnComplete = vi.fn();
    render(<ActionItemCard item={mockItem} onComplete={mockOnComplete} />);

    // The date should be rendered in a time element
    const timeElement = document.querySelector('time');
    expect(timeElement).toBeInTheDocument();
    expect(timeElement).toHaveAttribute('dateTime', '2024-01-01T00:00:00Z');
  });
});

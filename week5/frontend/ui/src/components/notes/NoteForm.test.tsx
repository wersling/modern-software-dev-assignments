import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { NoteForm } from './NoteForm';

describe('NoteForm', () => {
  it('renders title and content input fields and submit button', () => {
    const mockOnSubmit = vi.fn();
    render(<NoteForm onSubmit={mockOnSubmit} />);

    expect(screen.getByPlaceholderText('Title')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Content')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Add' })).toBeInTheDocument();
  });

  it('submits the form with valid data', async () => {
    const mockOnSubmit = vi.fn().mockResolvedValue(undefined);
    render(<NoteForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByPlaceholderText('Title');
    const contentInput = screen.getByPlaceholderText('Content');
    const submitButton = screen.getByRole('button', { name: 'Add' });

    fireEvent.change(titleInput, { target: { value: 'Test Note' } });
    fireEvent.change(contentInput, { target: { value: 'Test Content' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: 'Test Note',
        content: 'Test Content',
      });
    });
  });

  it('does not submit when fields are empty', () => {
    const mockOnSubmit = vi.fn();
    render(<NoteForm onSubmit={mockOnSubmit} />);

    const submitButton = screen.getByRole('button', { name: 'Add' });
    fireEvent.click(submitButton);

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('trims whitespace from inputs', async () => {
    const mockOnSubmit = vi.fn().mockResolvedValue(undefined);
    render(<NoteForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByPlaceholderText('Title');
    const contentInput = screen.getByPlaceholderText('Content');
    const submitButton = screen.getByRole('button', { name: 'Add' });

    fireEvent.change(titleInput, { target: { value: '  Test Note  ' } });
    fireEvent.change(contentInput, { target: { value: '  Test Content  ' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: 'Test Note',
        content: 'Test Content',
      });
    });
  });

  it('clears form after successful submission', async () => {
    const mockOnSubmit = vi.fn().mockResolvedValue(undefined);
    render(<NoteForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByPlaceholderText('Title') as HTMLInputElement;
    const contentInput = screen.getByPlaceholderText('Content') as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: 'Add' });

    fireEvent.change(titleInput, { target: { value: 'Test Note' } });
    fireEvent.change(contentInput, { target: { value: 'Test Content' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(titleInput.value).toBe('');
      expect(contentInput.value).toBe('');
    });
  });

  it('disables submit button while submitting', async () => {
    const mockOnSubmit = vi.fn().mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );
    render(<NoteForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByPlaceholderText('Title');
    const contentInput = screen.getByPlaceholderText('Content');
    const submitButton = screen.getByRole('button', { name: 'Add' });

    fireEvent.change(titleInput, { target: { value: 'Test Note' } });
    fireEvent.change(contentInput, { target: { value: 'Test Content' } });
    fireEvent.click(submitButton);

    // Button should be disabled immediately after click
    expect(submitButton).toBeDisabled();
    expect(screen.getByText('Adding...')).toBeInTheDocument();
  });
});

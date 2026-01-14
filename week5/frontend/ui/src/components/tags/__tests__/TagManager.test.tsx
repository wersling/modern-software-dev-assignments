import { describe, it, expect, vi, beforeEach, beforeAll } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ToastContainer } from 'react-toastify';
import { TagManager } from '../TagManager';
import * as tagsApiModule from '../../../services/tagsApi';

// Mock the tagsApi
vi.mock('../../../services/tagsApi', () => ({
  tagsApi: {
    list: vi.fn(),
    create: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('TagManager Component', () => {
  const mockTags = [
    { id: 1, name: 'work', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'urgent', created_at: '2024-01-01T00:00:00Z' },
    { id: 3, name: 'personal', created_at: '2024-01-01T00:00:00Z' },
  ];

  beforeAll(() => {
    vi.spyOn(tagsApiModule.tagsApi, 'list').mockResolvedValue(mockTags);
  });

  const defaultProps = {
    onTagCreated: vi.fn(),
    onTagDeleted: vi.fn(),
    showStats: false,
  };

  const renderWithToast = (component: React.ReactElement) => {
    render(
      <>
        {component}
        <ToastContainer />
      </>
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders collapsed by default', () => {
    renderWithToast(<TagManager {...defaultProps} />);
    expect(screen.getByText('🏷️ Manage Tags')).toBeInTheDocument();
    expect(screen.queryByText('All Tags')).not.toBeInTheDocument();
  });

  it('expands when toggle button is clicked', async () => {
    renderWithToast(<TagManager {...defaultProps} />);

    const toggleButton = screen.getByText('🏷️ Manage Tags');
    fireEvent.click(toggleButton);

    await waitFor(() => {
      expect(screen.getByText('All Tags')).toBeInTheDocument();
    });
  });

  it('displays tags when expanded', async () => {
    renderWithToast(<TagManager {...defaultProps} />);

    const toggleButton = screen.getByText('🏷️ Manage Tags');
    fireEvent.click(toggleButton);

    await waitFor(() => {
      expect(screen.getByText('#work')).toBeInTheDocument();
      expect(screen.getByText('#urgent')).toBeInTheDocument();
      expect(screen.getByText('#personal')).toBeInTheDocument();
    });
  });

  it('creates a new tag', async () => {
    vi.spyOn(tagsApiModule.tagsApi, 'create').mockResolvedValue({
      id: 4,
      name: 'important',
      created_at: '2024-01-01T00:00:00Z',
    });

    renderWithToast(<TagManager {...defaultProps} />);

    const toggleButton = screen.getByText('🏷️ Manage Tags');
    fireEvent.click(toggleButton);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('New tag name')).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText('New tag name');
    const form = input.closest('form');

    if (form) {
      fireEvent.input(input, { target: { value: 'important' } });
      fireEvent.submit(form);

      await waitFor(() => {
        expect(tagsApiModule.tagsApi.create).toHaveBeenCalledWith('important');
      });
    }
  });

  it('validates tag name with spaces', async () => {
    renderWithToast(<TagManager {...defaultProps} />);

    const toggleButton = screen.getByText('🏷️ Manage Tags');
    fireEvent.click(toggleButton);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('New tag name')).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText('New tag name') as HTMLInputElement;
    const form = input.closest('form');

    if (form) {
      fireEvent.input(input, { target: { value: 'invalid tag name' } });
      fireEvent.submit(form);

      // Should not call create
      expect(tagsApiModule.tagsApi.create).not.toHaveBeenCalled();
    }
  });

  it('deletes a tag when delete button is clicked', async () => {
    vi.spyOn(tagsApiModule.tagsApi, 'delete').mockResolvedValue(undefined);

    // Mock window.confirm
    Object.defineProperty(window, 'confirm', {
      value: vi.fn(() => true),
      writable: true,
    });

    renderWithToast(<TagManager {...defaultProps} />);

    const toggleButton = screen.getByText('🏷️ Manage Tags');
    fireEvent.click(toggleButton);

    await waitFor(() => {
      expect(screen.getByText('#work')).toBeInTheDocument();
    });

    // Find the delete button for 'work' tag
    const workTag = screen.getByText('#work').parentElement;
    if (workTag) {
      const deleteButton = workTag.querySelector('[aria-label*="Delete"]');
      if (deleteButton) {
        fireEvent.click(deleteButton);

        await waitFor(() => {
          expect(tagsApiModule.tagsApi.delete).toHaveBeenCalledWith(1);
        });
      }
    }
  });

  it('shows management tips', async () => {
    renderWithToast(<TagManager {...defaultProps} />);

    const toggleButton = screen.getByText('🏷️ Manage Tags');
    fireEvent.click(toggleButton);

    await waitFor(() => {
      expect(screen.getByText(/💡 Tag Management Tips:/i)).toBeInTheDocument();
      expect(screen.getByText(/Tag names must start with a letter or number/i)).toBeInTheDocument();
      expect(screen.getByText(/Tag names cannot contain spaces/i)).toBeInTheDocument();
    });
  });
});

import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ToastContainer } from 'react-toastify';
import { TagFilter } from '../TagFilter';
import * as tagsApiModule from '../../../services/tagsApi';

// Mock the tagsApi
vi.mock('../../../services/tagsApi', () => ({
  tagsApi: {
    list: vi.fn(),
  },
}));

describe('TagFilter Component', () => {
  const mockTags = [
    { id: 1, name: 'work', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'urgent', created_at: '2024-01-01T00:00:00Z' },
    { id: 3, name: 'personal', created_at: '2024-01-01T00:00:00Z' },
  ];

  beforeAll(() => {
    vi.spyOn(tagsApiModule.tagsApi, 'list').mockResolvedValue(mockTags);
  });

  const defaultProps = {
    selectedTagIds: [],
    onTagToggle: vi.fn(),
    onClearFilters: vi.fn(),
    disabled: false,
    filterMode: 'OR' as const,
    onFilterModeChange: vi.fn(),
  };

  const renderWithToast = (component: React.ReactElement) => {
    render(
      <>
        {component}
        <ToastContainer />
      </>
    );
  };

  it('renders loading state', () => {
    renderWithToast(<TagFilter {...defaultProps} />);
    expect(screen.getByText('Loading tags...')).toBeInTheDocument();
  });

  it('renders tags when loaded', async () => {
    renderWithToast(<TagFilter {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('Filter by Tags')).toBeInTheDocument();
    });
  });

  it('calls onTagToggle when tag is clicked', async () => {
    renderWithToast(<TagFilter {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('#work')).toBeInTheDocument();
    });

    const workTag = screen.getByText('#work');
    fireEvent.click(workTag);

    expect(defaultProps.onTagToggle).toHaveBeenCalledWith(1);
  });

  it('shows active filters indicator when tags are selected', async () => {
    const props = {
      ...defaultProps,
      selectedTagIds: [1, 2],
    };

    renderWithToast(<TagFilter {...props} />);

    await waitFor(() => {
      expect(screen.getByText(/Filtering by:/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/work, urgent/)).toBeInTheDocument();
  });

  it('displays "Clear Filters" button when filters are active', async () => {
    const props = {
      ...defaultProps,
      selectedTagIds: [1],
    };

    renderWithToast(<TagFilter {...props} />);

    await waitFor(() => {
      expect(screen.getByText('Clear Filters')).toBeInTheDocument();
    });
  });

  it('calls onClearFilters when clear button is clicked', async () => {
    const props = {
      ...defaultProps,
      selectedTagIds: [1],
    };

    renderWithToast(<TagFilter {...props} />);

    await waitFor(() => {
      const clearButton = screen.getByText('Clear Filters');
      fireEvent.click(clearButton);
      expect(props.onClearFilters).toHaveBeenCalled();
    });
  });
});

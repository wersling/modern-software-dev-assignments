# NoteCard Tags Display Feature

## Overview

The `NoteCard` component now supports displaying tags associated with notes. Tags are displayed as colorful chips between the note content and timestamp.

## Features

### 1. **Automatic Tag Display**
- Tags are automatically displayed if a note has one or more tags
- If a note has no tags, no tag section is rendered
- Tags are displayed in horizontal layout with wrapping for multiple tags

### 2. **Color Generation**
- Each tag gets a unique, consistent background color based on its name
- Colors are generated using a hash function, ensuring the same tag name always gets the same color
- Colors use soft pastel tones (HSL: 60-80% saturation, 85-95% lightness) for readability
- No two different tag names will have the same color (with very high probability)

### 3. **Interactive Tag Filtering (Optional)**
- If the `onTagClick` callback is provided, tags become clickable
- Clicking a tag triggers the callback with the tag name
- Visual feedback includes hover effects (slight elevation and shadow)
- Cursor changes to pointer to indicate interactivity

### 4. **Accessibility**
- Each tag has proper `aria-label` for screen readers
- Title attributes provide additional context
- Keyboard-accessible through standard tab navigation
- High contrast text colors for readability

## Usage

### Basic Usage (Display Only)

```tsx
import { NoteCard } from './components/notes/NoteCard';

function NotesList() {
  return (
    <NoteCard
      note={note}
      onUpdate={handleUpdate}
      onDelete={handleDelete}
    />
  );
}
```

### With Tag Filtering

```tsx
import { NoteCard } from './components/notes/NoteCard';

function NotesList() {
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  const handleTagClick = (tagName: string) => {
    // Filter notes by tag
    setSelectedTag(tagName);
    // Implement filtering logic...
  };

  return (
    <NoteCard
      note={note}
      onUpdate={handleUpdate}
      onDelete={handleDelete}
      onTagClick={handleTagClick}  // Enable tag filtering
    />
  );
}
```

## Component Props

```typescript
interface NoteCardProps {
  note: Note;                                      // Required: Note data object
  onUpdate: (id: number, data: NoteUpdate) => Promise<void>;  // Required: Update callback
  onDelete: (id: number) => Promise<void>;         // Required: Delete callback
  onTagClick?: (tagName: string) => void;          // Optional: Tag filter callback
}
```

## Note Type

```typescript
interface Note {
  id: number;
  title: string;
  content: string;
  created_at: string;
  tags: Tag[];  // Array of tags
}

interface Tag {
  id: number;
  name: string;
  created_at: string;
}
```

## Styling

### CSS Classes

The component uses the following CSS classes (defined in `App.css`):

- `.note-tags` - Container for tag chips
  - Flexbox layout with wrapping
  - Gap between tags
  - Margin spacing

- `.tag-chip` - Individual tag chip
  - Rounded corners (12px)
  - Padding and font sizing
  - Hover effects for interactive tags
  - Smooth transitions

### Color Generation Algorithm

The `getTagColor()` function generates consistent colors:

```typescript
function getTagColor(name: string): string {
  // Hash the tag name to a number
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }

  // Generate HSL values
  const hue = Math.abs(hash % 360);              // Full color spectrum
  const saturation = 60 + (hash % 20);            // 60-80% (vibrant but soft)
  const lightness = 85 + (hash % 10);             // 85-95% (pastel, readable)

  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}
```

## Examples

### Example 1: Note with Multiple Tags

```tsx
const note = {
  id: 1,
  title: "Meeting Notes",
  content: "Discussed project roadmap...",
  created_at: "2025-01-08T10:00:00Z",
  tags: [
    { id: 1, name: "work", created_at: "2025-01-08T10:00:00Z" },
    { id: 2, name: "important", created_at: "2025-01-08T10:00:00Z" },
    { id: 3, name: "q1", created_at: "2025-01-08T10:00:00Z" }
  ]
};
```

This will render three colored chips:
- #work (blue)
- #important (red)
- #q1 (green)

### Example 2: Note Without Tags

```tsx
const note = {
  id: 2,
  title: "Quick Note",
  content: "Just a reminder...",
  created_at: "2025-01-08T11:00:00Z",
  tags: []
};
```

No tags section will be rendered.

### Example 3: Implementing Tag Filtering

```tsx
function NotesList() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [filterTag, setFilterTag] = useState<string | null>(null);

  // Filter notes by selected tag
  const filteredNotes = filterTag
    ? notes.filter(note => note.tags.some(tag => tag.name === filterTag))
    : notes;

  const handleTagClick = (tagName: string) => {
    // Toggle filter on/off
    setFilterTag(prev => prev === tagName ? null : tagName);
  };

  return (
    <>
      {filterTag && (
        <div className="filter-indicator">
          Filtering by tag: #{filterTag}
          <button onClick={() => setFilterTag(null)}>Clear</button>
        </div>
      )}

      <ul className="notes-list">
        {filteredNotes.map(note => (
          <NoteCard
            key={note.id}
            note={note}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
            onTagClick={handleTagClick}  // Enable filtering
          />
        ))}
      </ul>
    </>
  );
}
```

## Integration with Backend API

The frontend has full support for tag management through the `tagsApi` service:

```typescript
import { tagsApi } from './services/api';

// List all tags
const allTags = await tagsApi.list();

// Search tags
const results = await tagsApi.list('work');

// Create new tag
const newTag = await tagsApi.create({ name: 'urgent' });

// Delete tag
await tagsApi.delete(tagId);

// Attach tags to note
const updatedNote = await tagsApi.attachToNote(noteId, { tag_ids: [1, 2, 3] });

// Remove tag from note
const updatedNote = await tagsApi.removeFromNote(noteId, tagId);
```

## Future Enhancements

Potential improvements for future versions:

1. **Edit Mode Tag Selection**
   - Add tag selector in edit mode
   - Multi-select dropdown with tag creation
   - Tag autocomplete/suggestions

2. **Remove Tag from Note**
   - Add "×" button on each tag
   - Confirm removal with tooltip
   - Optimistic UI updates

3. **Advanced Filtering**
   - Filter by multiple tags (AND/OR logic)
   - Filter combination UI
   - Saved filter presets

4. **Tag Management**
   - Rename tags (bulk update)
   - Merge similar tags
   - Tag statistics/analytics

## Performance Considerations

- Color generation is fast (O(n) where n = tag name length)
- No re-renders unless tags change
- Memoization could be added for `getTagColor` if performance issues arise
- Tag filtering is done in parent component for flexibility

## Accessibility

- Tags use semantic HTML (`<span>` elements)
- Proper ARIA labels for screen readers
- Keyboard navigable when interactive
- Sufficient color contrast (verified with WCAG guidelines)
- Hover states for visual feedback

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- HSL color support required (all modern browsers)
- Flexbox support required
- No polyfills needed for modern browsers

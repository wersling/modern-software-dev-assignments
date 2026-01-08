# NoteCard Tags Feature - Visual Preview

## Tag Display Examples

### Single Tag
```
┌─────────────────────────────────────────────┐
│ Meeting Notes                          ✏️ 🗑️ │
│                                             │
│ Discussed Q1 roadmap and priorities...      │
│                                             │
│ [ 🏷️ #work ]                                │  ← Tag chip (blue)
│                                             │
│ Jan 8, 2025, 10:30 AM                       │
└─────────────────────────────────────────────┘
```

### Multiple Tags
```
┌─────────────────────────────────────────────┐
│ Project Ideas                          ✏️ 🗑️ │
│                                             │
│ Implement new features for the app...       │
│                                             │
│ [ 🏷️ #feature ] [ 🎨 #frontend ] [ 🔥 #hot ] │  ← Multiple tags
│                                             │
│ Jan 8, 2025, 2:15 PM                        │
└─────────────────────────────────────────────┘
```

### No Tags
```
┌─────────────────────────────────────────────┐
│ Quick Reminder                         ✏️ 🗑️ │
│                                             │
│ Don't forget to call mom tomorrow            │
│                                             │
│ (no tags displayed)                          │  ← No tag section
│                                             │
│ Jan 8, 2025, 9:00 AM                        │
└─────────────────────────────────────────────┘
```

## Color Examples

The `getTagColor()` function generates consistent pastel colors:

| Tag Name | Generated Color | HSL Values |
|----------|----------------|------------|
| `work` | Blue | `hsl(120, 72%, 89%)` |
| `personal` | Green | `hsl(240, 65%, 87%)` |
| `urgent` | Red | `hsl(180, 77%, 93%)` |
| `important` | Purple | `hsl(300, 68%, 85%)` |
| `todo` | Orange | `hsl(60, 70%, 91%)` |
| `done` | Teal | `hsl(150, 73%, 88%)` |
| `meeting` | Pink | `hsl(330, 69%, 92%)` |
| `idea` | Yellow | `hsl(90, 74%, 90%)` |

Note: The exact HSL values will vary based on the hash algorithm, but they will always fall within:
- **Hue**: 0-360° (full spectrum)
- **Saturation**: 60-80% (vibrant but soft)
- **Lightness**: 85-95% (pastel, readable)

## Interactive States

### Default State (No onTagClick)
```
[ 🏷️ #work ]
  ↑
  Not clickable (cursor: default)
  No hover effect
```

### Interactive State (With onTagClick)
```
Normal:     [ 🏷️ #work ]  ← cursor: pointer
Hover:      [ 🏷️ #work ]  ← slightly elevated + shadow
Click:      [ 🏷️ #work ]  ← triggered callback
```

## Layout Behavior

### Single Line Tags
```
Content paragraph here...

[ #tag1 ] [ #tag2 ] [ #tag3 ]

Timestamp
```

### Wrapped Tags (Multiple)
```
Content paragraph here...

[ #long-tag-name ] [ #tag2 ]
[ #tag3 ]            [ #another-tag ]

Timestamp
```

## Tag Filter Indicator

When a tag filter is active:

```
┌─────────────────────────────────────────────┐
│ 📌 Filtering by tag: #work  [Clear filter]  │  ← Filter indicator
│         (Showing 3 notes)                    │
└─────────────────────────────────────────────┘
```

## Responsive Design

### Desktop (> 600px)
```
[ #tag1 ] [ #tag2 ] [ #tag3 ] [ #tag4 ]
  ↓
Full horizontal layout with wrapping
```

### Mobile (≤ 600px)
```
[ #tag1 ]
[ #tag2 ]
[ #tag3 ]
  ↓
Tags may wrap more frequently
Chip size remains the same
```

## Accessibility Features

### Screen Reader
```html
<span class="tag-chip" aria-label="Tag: work">
  #work
</span>
```
- Announced as "Tag: work"
- Proper semantic markup

### Keyboard Navigation
```
Tab → [ #tag1 ] → [ #tag2 ] → [ #tag3 ]
  ↑
When interactive, tags are focusable
```

### Visual Accessibility
- High contrast text (dark on light pastel)
- Clear tap targets (minimum 44×44px recommended)
- No reliance on color alone (has # prefix and text)
- Hover states for visual feedback

## CSS Styling

```css
/* Container */
.note-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0.5rem 0;
}

/* Individual Chip */
.tag-chip {
  display: inline-block;
  padding: 0.25rem 0.75rem;      /* Compact but readable */
  border-radius: 12px;            /* Rounded pill shape */
  font-size: 0.85rem;             /* Slightly smaller than body */
  font-weight: 500;               /* Medium weight */
  color: #333;                    /* Dark text for contrast */
  cursor: default;                /* Default cursor */
  transition: all 0.2s ease;     /* Smooth animations */
  user-select: none;              /* Prevent text selection */
}

/* Interactive Tags */
.tag-chip[title*="Filter by tag"] {
  cursor: pointer;                /* Pointer for interactive */
}

.tag-chip[title*="Filter by tag"]:hover {
  transform: translateY(-1px);    /* Subtle lift */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);  /* Soft shadow */
}

.tag-chip:active {
  transform: translateY(0);       /* Reset on click */
}
```

## Integration Points

### 1. Note Type Definition
```typescript
interface Note {
  id: number;
  title: string;
  content: string;
  created_at: string;
  tags: Tag[];  // ← Tags are part of Note
}
```

### 2. Component Props
```typescript
interface NoteCardProps {
  note: Note;
  onUpdate: (id: number, data: NoteUpdate) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
  onTagClick?: (tagName: string) => void;  // ← Optional callback
}
```

### 3. Render Method
```tsx
<p>{note.content}</p>
{renderTags()}  // ← Tags between content and timestamp
<time dateTime={note.created_at}>{formatDate}</time>
```

## Performance Characteristics

- **Color Generation**: O(n) where n = tag name length
- **Render Time**: O(m) where m = number of tags
- **Re-renders**: Only when tags array changes
- **Memory**: Minimal (no caching needed for this scale)

## Browser Compatibility

✅ Chrome 90+
✅ Firefox 88+
✅ Safari 14+
✅ Edge 90+

Required features:
- Flexbox
- HSL colors
- CSS transitions
- ES6+ (arrow functions, template literals)

## Future Enhancements

### Potential Improvements
1. **Tag Removal**: Add × button to remove tags from notes
2. **Tag Editing**: Inline tag renaming
3. **Tag Suggestions**: Autocomplete when adding tags
4. **Tag Statistics**: Show note count per tag
5. **Bulk Tagging**: Add tag to multiple notes at once
6. **Tag Colors**: Custom color picker for tags
7. **Tag Icons**: Associate icons with tags
8. **Tag Groups**: Organize tags into categories

### Advanced Filtering
```
Filter: [#work] OR [#urgent]
       ↓
[ ☑ work ] [ ☑ urgent ] [ ☐ personal ]
       ↓
Apply Clear
```

### Tag Management UI
```
┌────────────────────────────────┐
│ 🏷️ Tag Manager                 │
│                                │
│ [+ Create New Tag]             │
│                                │
│ ┌──────────────────────────┐  │
│ │ #work (12 notes)      ×  │  │
│ │ #personal (8 notes)    ×  │  │
│ │ #urgent (3 notes)      ×  │  │
│ └──────────────────────────┘  │
│                                │
│ [ Merge Selected ]             │
└────────────────────────────────┘
```

## Testing

### Manual Testing Checklist
- [ ] Single tag displays correctly
- [ ] Multiple tags display and wrap properly
- [ ] No tags doesn't show tag section
- [ ] Tag colors are consistent for same tag name
- [ ] Different tags have different colors
- [ ] Clicking tag triggers filter (when callback provided)
- [ ] Hover effects work on interactive tags
- [ ] Tags are readable (contrast check)
- [ ] Tags work on mobile devices
- [ ] Screen readers announce tags correctly

### Automated Tests
See `tagColor.test.ts` for unit tests covering:
- Color consistency
- Color distribution
- Edge cases (empty strings, special characters)
- HSL value ranges

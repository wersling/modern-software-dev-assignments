# Modern Software Dev Starter - React Frontend

This is the React frontend for the Modern Software Dev Starter (Week 5) project. It's built with Vite, React 19, and TypeScript, providing a modern and efficient development experience.

## Tech Stack

- **React 19** - Latest React features with hooks and concurrent rendering
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool with Hot Module Replacement (HMR)
- **Vitest** - Unit testing framework with React Testing Library
- **CSS Modules** - Scoped styling for components

## Project Structure

```
src/
├── components/
│   ├── notes/
│   │   ├── NoteCard.tsx          # Single note display
│   │   ├── NoteForm.tsx          # Note creation form
│   │   ├── NotesList.tsx         # Notes list with CRUD
│   │   └── NoteForm.test.tsx     # Component tests
│   └── action-items/
│       ├── ActionItemCard.tsx    # Single action item display
│       ├── ActionItemForm.tsx    # Action item creation form
│       ├── ActionItemsList.tsx   # Action items list with CRUD
│       └── ActionItemCard.test.tsx # Component tests
├── services/
│   └── api.ts                    # API client with fetch
├── types/
│   └── index.ts                  # TypeScript type definitions
├── test/
│   └── setup.ts                  # Test configuration
├── App.tsx                       # Main application component
├── App.css                       # Component styles
├── index.css                     # Global styles
└── main.tsx                      # Application entry point
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

From the project root directory:

```bash
make web-install
```

Or directly:

```bash
cd frontend/ui
npm install
```

### Development Server

Start the development server (runs on http://localhost:3000):

```bash
make web-dev
```

Or directly:

```bash
cd frontend/ui
npm run dev
```

The dev server proxies API requests to the FastAPI backend at `http://127.0.0.1:8000`.

### Building for Production

Build the React app for production:

```bash
make web-build
```

Or directly:

```bash
cd frontend/ui
npm run build
```

The build output will be in `frontend/dist/`, which is served by the FastAPI backend.

### Running Tests

Run unit tests:

```bash
make web-test
```

Or with UI:

```bash
make web-test-ui
```

Or directly:

```bash
cd frontend/ui
npm run test
npm run test:ui  # Interactive UI
```

## Environment Variables

Create a `.env` file in the `frontend/ui` directory:

```env
# API base URL (optional, defaults to empty string for relative URLs)
VITE_API_BASE_URL=
```

For development, leave `VITE_API_BASE_URL` empty to use the Vite proxy. For production, set it to your backend URL if the frontend and backend are served from different domains.

## API Integration

The frontend communicates with the FastAPI backend using the following endpoints:

### Notes
- `GET /notes/` - List all notes
- `POST /notes/` - Create a new note
- `GET /notes/{id}` - Get a specific note
- `GET /notes/search/?q=query` - Search notes

### Action Items
- `GET /action-items/` - List all action items
- `POST /action-items/` - Create a new action item
- `PUT /action-items/{id}/complete` - Mark an action item as completed

## Features

### Optimistic UI Updates

Both Notes and Action Items lists use optimistic updates:
- New items appear immediately in the list
- UI updates before server confirmation
- Automatic rollback on error

### Error Handling

- User-friendly error messages
- Retry functionality for failed requests
- Loading states for async operations

### Responsive Design

- Mobile-friendly layout
- Adaptive forms and lists
- Touch-friendly buttons and inputs

## Component Architecture

### Notes Components

**NoteForm**
- Handles note creation with title and content
- Form validation and error handling
- Loading state during submission

**NoteCard**
- Displays individual note with formatted date
- Clean, card-based layout

**NotesList**
- Manages notes state and API calls
- Implements optimistic updates
- Error handling with retry button

### Action Items Components

**ActionItemForm**
- Handles action item creation
- Simple description input
- Form validation

**ActionItemCard**
- Displays action item with status indicator
- Complete button for uncompleted items
- Visual distinction between open/done states

**ActionItemsList**
- Manages action items state
- Implements optimistic updates
- Handles completion status changes

## Testing

The project uses Vitest and React Testing Library for unit testing.

### Running Tests

```bash
npm run test          # Run tests once
npm run test:ui       # Interactive test UI
npm run test:watch    # Watch mode
```

### Test Files

- `NoteForm.test.tsx` - Tests for note creation form
- `ActionItemCard.test.tsx` - Tests for action item card component

## Development Tips

### Hot Module Replacement (HMR)

Vite provides instant HMR. Changes to React components are reflected immediately without full page reload.

### TypeScript Strict Mode

The project uses TypeScript strict mode for maximum type safety. All components are fully typed.

### Code Quality

```bash
npm run lint          # Run ESLint
```

## Deployment

The frontend is built and served by the FastAPI backend:

1. Build the frontend: `npm run build`
2. Start the FastAPI backend: `make run` (from project root)
3. Access the app at `http://localhost:8000`

The backend serves the static React files from `frontend/dist/` and provides API endpoints.

## Production Considerations

- The build is optimized and minified
- Static assets are hashed for caching
- API requests use relative URLs in production
- SPA routing is handled by FastAPI fallback

## Future Enhancements

Potential improvements for the frontend:

- Add client-side routing with React Router
- Implement search and filtering UI
- Add loading skeletons
- Implement infinite scroll for lists
- Add toasts/notifications for user feedback
- Implement undo/redo for optimistic updates
- Add dark mode support
- PWA capabilities

## Troubleshooting

### Port Already in Use

If port 3000 is in use:
```bash
# Kill the process
lsof -ti:3000 | xargs kill -9

# Or use a different port in vite.config.ts
```

### API Connection Issues

Ensure the FastAPI backend is running on port 8000:
```bash
make run  # From project root
```

### Build Errors

Clear the cache and rebuild:
```bash
rm -rf node_modules dist .vite
npm install
npm run build
```

## License

This project is part of the Modern Software Dev Starter curriculum.

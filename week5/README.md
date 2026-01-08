# Week 5

Minimal full‑stack starter for experimenting with autonomous coding agents.

- **Backend**: FastAPI with SQLite (SQLAlchemy 2.0)
- **Frontend**: Vite + React 19 + TypeScript
- **Testing**: pytest (backend) + Vitest + React Testing Library (frontend)
- **Code Quality**: Black + Ruff + Pre-commit hooks
- **Tasks**: Open-ended challenges for practicing agent-driven workflows

## Features

### Notes
- ✅ Create, read, update, delete notes
- ✅ Full-text search
- ✅ Optimistic UI updates
- ✅ Real-time form validation

### Action Items
- ✅ Create, list, and complete action items
- ✅ Filter by status (All/Active/Completed)
- ✅ Bulk complete multiple items
- ✅ Optimistic UI updates
- ✅ Enhanced validation (1-1000 characters)

## Quickstart

### 1) Backend Setup

Create and activate a virtualenv, then install dependencies:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

(Optional) Install pre-commit hooks:

```bash
pre-commit install
```

### 2) Frontend Setup

```bash
make web-install
```

### 3) Run the Application

**Development mode** (recommended for active development):

```bash
# Terminal 1: Start backend
make run

# Terminal 2: Start frontend dev server
make web-dev
```

- Frontend: http://localhost:3001
- Backend API: http://localhost:8000/docs

**Production mode**:

```bash
# Build frontend
make web-build

# Start backend (serves both API and frontend)
make run
```

- Application: http://localhost:8000
- API docs: http://localhost:8000/docs

## Structure

```
backend/                # FastAPI application
├── app/
│   ├── routers/       # API endpoints
│   ├── models.py      # SQLAlchemy models
│   ├── schemas.py     # Pydantic schemas
│   └── db.py          # Database configuration
└── tests/             # Backend tests

frontend/              # Frontend assets
├── ui/                # Vite + React application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API client
│   │   └── types/       # TypeScript types
│   └── dist/            # Production build (served by FastAPI)
└── MIGRATION_SUMMARY.md

data/                  # SQLite database + seed data
docs/                  # TASKS.md for agent-driven workflows
```

## Tests

### Backend Tests

```bash
make test
```

### Frontend Tests

```bash
make web-test          # Run tests
make web-test-ui       # Run tests with UI
```

## Formatting/Linting

```bash
cd week5 && make format
cd week5 && make lint
```

## Available Make Targets

```bash
make run            # Start backend server
make test           # Run backend tests
make format         # Format code (black + ruff)
make lint           # Check code quality
make seed           # Seed database with sample data
make web-install    # Install frontend dependencies
make web-dev        # Start frontend dev server
make web-build      # Build frontend for production
make web-test       # Run frontend tests
make web-test-ui    # Run frontend tests with UI
```

## Configuration

### Backend
Copy `.env.example` to `.env` (in `week5/`) to override defaults like the database path.

### Frontend
Copy `frontend/ui/.env.example` to `frontend/ui/.env` to configure API base URL:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Documentation

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Frontend Guide**: See `frontend/ui/README.md` for detailed React documentation
- **Tasks List**: See `docs/TASKS.md` for open-ended challenges

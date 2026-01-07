.PHONY: run test format lint seed web-install web-dev web-build web-test

run:
	PYTHONPATH=. uvicorn backend.app.main:app --reload --host $${HOST:-127.0.0.1} --port $${PORT:-8000}

test:
	PYTHONPATH=. pytest -q backend/tests

format:
	black .
	ruff check . --fix

lint:
	ruff check .

seed:
	PYTHONPATH=. python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"

# Frontend targets
web-install:
	cd frontend/ui && npm install

web-dev:
	cd frontend/ui && npm run dev

web-build:
	cd frontend/ui && npm run build

web-test:
	cd frontend/ui && npm run test

web-test-ui:
	cd frontend/ui && npm run test:ui


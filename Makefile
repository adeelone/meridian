.PHONY: install dev cli test lint format typecheck clean

install:
	python -m pip install -e ".[dev,redis,llm]"
	cd packages/frontend && npm install

dev:
	python -m uvicorn app.main:app --app-dir packages/backend --reload --port 8000 & cd packages/frontend && npm run dev

cli:
	python -m pip install -e .

test:
	python -m pytest
	cd packages/frontend && npm test

lint:
	python -m ruff check packages tests
	cd packages/frontend && npm run lint

format:
	python -m black packages tests
	python -m ruff check --fix packages tests

typecheck:
	python -m mypy packages/core packages/backend packages/cli
	cd packages/frontend && npm run build

clean:
	python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache','.mypy_cache','.ruff_cache','htmlcov','packages/frontend/dist']]"

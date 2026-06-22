.PHONY: install run test lint

install:
	uv sync

run:
	uv run python main.py

test:
	uv run pytest -q

lint:
	uv run ruff check .
	uv run ruff format --check .

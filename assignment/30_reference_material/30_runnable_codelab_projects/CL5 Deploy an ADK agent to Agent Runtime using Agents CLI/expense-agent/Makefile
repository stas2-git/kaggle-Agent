.PHONY: install test lint playground generate-traces grade dry-run

install:
	uv sync --all-extras

test:
	uv run pytest tests/unit tests/integration -q

lint:
	uv run ruff check .
	uv run ruff format --check .

playground:
	agents-cli playground

generate-traces:
	uv run python tests/eval/generate_traces.py

grade:
	agents-cli eval grade \
		--config tests/eval/eval_config.yaml \
		--traces artifacts/traces/generated_traces.json

dry-run:
	agents-cli deploy --dry-run

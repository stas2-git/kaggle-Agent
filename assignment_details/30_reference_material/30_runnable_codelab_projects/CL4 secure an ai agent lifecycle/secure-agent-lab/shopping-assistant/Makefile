.PHONY: install test lint security playground generate-traces grade

install:
	uv sync --all-extras

test:
	uv run pytest tests -q

lint:
	uv run ruff check .
	uv run ruff format --check .

security:
	uv run semgrep --error --config .semgrep/rules.yaml app tests

playground:
	agents-cli playground

generate-traces:
	uv run python tests/eval/generate_traces.py

grade:
	agents-cli eval grade \
		--config tests/eval/eval_config.yaml \
		--traces artifacts/traces/generated_traces.json

.PHONY: install playground serve test lint generate-traces grade

install:
	uv sync --all-extras

playground:
	uv run python -m expense_agent.fast_api_app

serve: playground

test:
	uv run pytest tests/unit tests/integration -q

lint:
	uv run ruff check .
	uv run ruff format --check .

generate-traces:
	uv run python tests/eval/generate_traces.py

grade:
	agents-cli eval grade \
		--config tests/eval/eval_config.yaml \
		--traces artifacts/traces/generated_traces.json

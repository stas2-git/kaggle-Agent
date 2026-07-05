PORT ?= 8080

.PHONY: install run run-offline api test integration lint generate-traces grade eval

install:
	uv sync

run:
	agents-cli run "Review the approved loss-ratio-spike demo portfolio for 2026-06."

run-offline:
	uv run python -m portfolio_agent.run --input tests/golden/loss_ratio_spike.csv --latest-month 2026-06 --force-offline

api:
	uv run uvicorn portfolio_agent.fast_api_app:app --host 127.0.0.1 --port $(PORT)

test:
	uv run pytest -q

integration:
	uv run pytest tests/integration -q

lint:
	uv run python -m compileall -q portfolio_agent tests

generate-traces:
	agents-cli eval generate

grade:
	agents-cli eval grade

eval: generate-traces grade

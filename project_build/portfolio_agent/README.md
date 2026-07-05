# Portfolio Agent Package

This package is organized as a pyramid: entry points at the top, shared orchestration in
the middle, and single-purpose layers below. Start at the top and only open a lower layer
when you need to change what it does.

## Entry points (pick one, based on how the agent is invoked)

| File | Invoked by | Role |
|---|---|---|
| `agent.py` | `agents-cli run`, ADK runtime | Exports `root_agent` and `app` — the ADK-facing entry point. |
| `run.py` | `make run` / `make run-offline`, `python -m portfolio_agent.run` | CLI entry point. |
| `fast_api_app.py` | `make api`, `uvicorn portfolio_agent.fast_api_app:app` | HTTP entry point (`/healthz`, `/readyz`, `POST /api/reviews`). |

All three entry points are thin adapters. None of them contain actuarial calculations,
threshold logic, or prompt policy — they parse/format around one shared call.

## Orchestration (what every entry point actually calls)

`service.py` — `review_portfolio(...)` is the single shared pipeline: load -> validate ->
calculate metrics -> detect anomalies -> investigate drivers -> synthesize findings ->
write report -> write trace. All three entry points call this and only this.

## Supporting layers

```text
core/            Deterministic domain logic - the actuarial engine itself
  tools.py         load/validate/calculate/detect/investigate functions
  schemas.py       Pydantic data contracts (MetricsRecord, AnomalyRecord, ReviewMemo, ...)
  security.py      path allowlisting, prompt-injection screening
  reporting.py     compiles the final markdown report

adk/             ADK-boundary plumbing (wraps core/ for model-callable use)
  adk_tools.py     JSON-safe tool adapters exposed to the model
  callbacks.py     before/after agent/model/tool policy enforcement

observability/   Run evidence
  tracing.py       JSON trace event logger

support/         Cross-cutting, low-churn utilities
  config.py        env/config loading (PortfolioAgentConfig)
  skill_context.py loads the portfolio_monitoring Agent Skill at runtime

app_utils/       ADK app scaffolding utilities (telemetry, typing) - not domain logic
```

## Why this split

- **`core/` has no ADK or FastAPI dependency.** It is the same deterministic engine
  regardless of how it's invoked, and it's what `tests/test_tools.py` and
  `tests/test_golden.py` exercise directly.
- **`adk/` depends on `core/`, never the reverse.** It exists only to give the model a
  JSON-safe, policy-enforced way to call into `core/`.
- **`agent.py`, `run.py`, `fast_api_app.py`, and `service.py` stay at the top level** because
  they are the package's public shape — `agents-cli` and `agents-cli-manifest.yaml` expect
  `portfolio_agent.agent:root_agent` to resolve without a deeper import path.

See `spec_files/10_core/02_agent_architecture.md` for the full architectural rationale and
`spec_files/20_contracts/02_tool_contracts.yaml` for the tool/callback contract this package
implements.

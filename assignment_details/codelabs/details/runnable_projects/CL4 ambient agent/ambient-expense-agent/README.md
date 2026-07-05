# Ambient Expense Agent

This is the completed CL4 codelab project: a secure ADK 2.0 graph workflow that accepts expense events, auto-approves safe expenses under $100 without an LLM, and sends expenses of $100 or more through Gemini risk review and human approval.

The security screen runs before routing. It redacts SSNs and credit-card numbers, records the redaction categories, and sends prompt-injection attempts directly to human review without exposing them to Gemini.

## Project layout

- `expense_agent/agent.py` — workflow, deterministic routing, security, Gemini reviewer, and HITL nodes
- `expense_agent/fast_api_app.py` — local ADK/FastAPI server and Pub/Sub trigger
- `expense_agent/config.py` — model and $100 threshold
- `tests/eval/` — five scenarios, trace generator, and two LLM-as-judge metrics
- `artifacts/traces/generated_traces.json` — latest generated five-case trace set

## Setup

Requires Python 3.11+, `uv`, and `agents-cli 0.5.x`.

```bash
cp .env.example .env
# Add GOOGLE_API_KEY to .env, or configure the Vertex AI variables.
make install
```

For Vertex AI authentication:

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

## Run locally

```bash
make playground
```

Open <http://localhost:8080/dev-ui/>. The ambient endpoint is:

```text
POST /apps/expense_agent/trigger/pubsub
```

Example low-value event:

```bash
curl -s http://localhost:8080/apps/expense_agent/trigger/pubsub \
  -H 'Content-Type: application/json' \
  -d "{\"message\":{\"data\":\"$(printf '%s' '{\"amount\":45,\"submitter\":\"bob@company.com\",\"category\":\"meals\",\"description\":\"Team lunch\",\"date\":\"2026-04-12\"}' | base64 | tr -d '\\n')\"},\"subscription\":\"projects/demo/subscriptions/test-sub\"}"
```

Inspect that user’s sessions at <http://localhost:8080/dev-ui/?app=expense_agent&userId=test-sub>.

## Verify and evaluate

```bash
make test
make generate-traces
make grade
```

`make grade` uses Agents CLI’s LLM-as-judge service and requires a configured Google Cloud project plus Application Default Credentials. An AI Studio API key is sufficient for agent inference, but not for the Agents CLI grading service.

This is a local prototype. It contains no deployment or cloud-infrastructure actions.

# Expense Agent for Agent Runtime

Completed local build for the CL5 Agent Runtime deployment codelab. The same ADK 2.0 graph is used locally and by the generated Agent Runtime `AdkApp` wrapper.

## Behavior

```text
Expense JSON
    |
    v
Parse and validate
    |
    v
Deterministic $100 router
    |
    +-- under $100 ----------> Python auto-approval
    |
    +-- $100 or more --------> Gemini risk review
                                  |
                                  v
                              RequestInput
                                  |
                                  v
                           Human approve/reject
```

## Project structure

- `app/agent.py` — deployment-neutral graph and business policy
- `app/agent_runtime_app.py` — generated Agent Runtime `AdkApp` wrapper
- `deployment/terraform/` — generated infrastructure and telemetry descriptors
- `deployment_metadata.json` — populated with the remote engine ID after deployment
- `tests/` — policy, runner, wrapper, and behavioral evaluation tests
- `artifacts/traces/generated_traces.json` — current local trace evidence

## Local setup and verification

```bash
cp .env.example .env
# Add GOOGLE_API_KEY for local model calls.
make install
make test
make lint
make generate-traces
```

Quick checks:

```bash
agents-cli run '{"data":{"amount":50,"submitter":"user@example.com","category":"meals","description":"Lunch","date":"2026-06-04"}}'

agents-cli run '{"data":{"amount":150,"submitter":"user@example.com","category":"meals","description":"Client dinner","date":"2026-06-04"}}'
```

## Deployment preparation

The runtime region is `us-west1`; Gemini location can remain `global`.

```bash
gcloud auth login --update-adc
gcloud config set project YOUR_PROJECT_ID

gcloud services enable \
  aiplatform.googleapis.com \
  cloudtrace.googleapis.com \
  cloudbuild.googleapis.com \
  agentregistry.googleapis.com \
  --project YOUR_PROJECT_ID

export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
export GOOGLE_CLOUD_LOCATION=global

agents-cli deploy --dry-run --project YOUR_PROJECT_ID --region us-west1
```

The local packaging check was also verified without cloud access using a placeholder project:

```bash
agents-cli deploy --dry-run --project local-test-project --region us-west1
```

## Actual deployment

Actual deployment creates billable external resources and is intentionally not executed by this build.

After tests and evaluation pass, run only with explicit approval:

```bash
agents-cli deploy \
  --project YOUR_PROJECT_ID \
  --region us-west1 \
  --no-wait

agents-cli deploy --status \
  --project YOUR_PROJECT_ID \
  --region us-west1
```

## Evaluation

```bash
make generate-traces
make grade
```

Local traces and deterministic route assertions pass. Managed Agents CLI grading requires a Google Cloud project and Application Default Credentials.

## Important architecture note

Agent Runtime hosts request-driven ADK agents and managed sessions. It does not accept Pub/Sub, Eventarc, or Cloud Scheduler triggers. For a truly event-driven ambient agent, deploy the trigger-facing service to Cloud Run or GKE and call Agent Runtime only if the split architecture is justified.

## Observability

After deployment, inspect:

- Cloud Trace for model and node latency
- Cloud Logging for runtime diagnostics
- `deployment_metadata.json` for the remote reasoning-engine resource ID

Cloud infrastructure was not provisioned and no remote deployment was performed.

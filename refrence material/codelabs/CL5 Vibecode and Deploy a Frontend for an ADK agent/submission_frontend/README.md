# Expense Manager Dashboard

Standalone FastAPI dashboard for the CL5 frontend codelab. It scans Agent Platform sessions for unresolved `adk_request_input` calls and resumes the exact Agent Runtime session after a manager decision.

## Local demo

```bash
cp .env.example .env
make install
make run
```

Open <http://localhost:8080>. Mock mode includes a normal travel expense and a security escalation.

```bash
make test
make lint
```

## Production configuration

Set `DASHBOARD_MODE=vertex`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and `AGENT_RUNTIME_ID`. The cloud gateway always uses `user_id="default-user"`.

## API

- `GET /` — dashboard UI
- `GET /api/pending` — unresolved approval requests
- `POST /api/action/{session_id}` — resume with `{approved, interrupt_id}`
- `GET /healthz` — liveness and configured mode

## Infrastructure

`infra/` defines the Cloud Run dashboard, service accounts, `roles/aiplatform.user` bindings, expense/dead-letter topics, and an OIDC-authenticated unwrapped push subscription to Agent Runtime `:query` with a ten-minute deadline and five-attempt dead-letter policy.

Build and publish the image, copy `terraform.tfvars.example`, and review a Terraform plan. Do not apply without explicit deployment approval.

## Security warning

The original codelab makes the manager dashboard publicly invokable. The Terraform default keeps it private. Production should use IAP or another authenticated manager identity, CSRF protection, authorization, audit logs, and idempotent decisions.

No Cloud Run service, IAM binding, API, topic, subscription, or Agent Runtime session was created or changed.

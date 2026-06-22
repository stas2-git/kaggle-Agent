# Secure Shopping Assistant

Completed CL4 secure-agent-lifecycle codelab project. It combines an ADK 2.0 shopping agent with deterministic discount policy, outcome-based tests, STRIDE threat modeling, command-execution guards, and Semgrep/pre-commit secret scanning.

## Architecture

```text
User prompt -> Gemini shopping agent -> redeem_discount tool
                                      -> Pydantic validation
                                      -> registered-user check
                                      -> atomic single-use check/update
                                      -> stable outcome returned to Gemini
```

Gemini may request the tool but cannot override its authorization or state rules.

## Setup

```bash
cp .env.example .env
# Put your Gemini API key in .env.
make install
```

## Quality and security gates

```bash
make test
make lint
make security
uv run pre-commit validate-config .pre-commit-config.yaml
```

This project lives inside an existing parent repository, so the build does not replace that repository’s Git hook. To use it as an independent lab repository, initialize Git inside this directory and then run:

```bash
uv run pre-commit install
```

The agent command gate is configured in `.agents/hooks.json`. It fails closed through `.agents/scripts/validate_tool_call.py`.

## Run the agent

```bash
agents-cli run "Redeem discount code WELCOME50 for registered user user_123."
# or
make playground
```

## Evaluation

```bash
make generate-traces
make grade
```

The local trace generator works with the configured Gemini API key. Agents CLI grading additionally requires a Google Cloud project and Application Default Credentials.

## Security artifacts

- `.agents/CONTEXT.md` — secure coding paved roads and TDD planning gate
- `.agents/hooks.json` — pre-tool command gate
- `.agents/skills/stride-threat-model/` — reusable local STRIDE skill
- `.semgrep/rules.yaml` — credential detection rule
- `implementation_plan.md` — security-aware build plan
- `threat_model.md` — executed STRIDE assessment
- `tests/test_agent.py` — outcome-based business/security tests

This is a local demonstration. Production needs authenticated identity, transactional persistence, idempotency, immutable audit logs, rate limiting, and CI enforcement.

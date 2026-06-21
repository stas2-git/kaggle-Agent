# Security and Privacy Spec

## Security objective

The agent must be useful without being dangerous. It should analyze approved synthetic data, produce local report artifacts, and preserve traceability. It must not access private systems, expose secrets, or perform external actions without human approval.

## Security model

The MVP uses a local, low-risk environment:

- Synthetic or deidentified data only.
- Local file reads only from approved directories.
- Local file writes only to approved output directories.
- No email sending.
- No production database connection.
- No hidden credentials in code, prompts, notebooks, or config files.

## Trust boundaries

| Boundary | Inside boundary | Outside boundary | Control |
|---|---|---|---|
| Data | Synthetic CSVs in `data/` | Real company data | Use demo data only |
| File reads | `data/`, `examples/` | Home directory, secrets, arbitrary files | Path allowlist |
| File writes | `outputs/` | Source files, system folders | Output allowlist |
| LLM context | Tool outputs and sanitized summaries | Raw untrusted notes, secrets, hidden files | Sanitization |
| External actions | None in MVP | Email, Slack, ticket creation | Disable or human approval |
| Configuration | Environment variables | Hardcoded keys | Secret scanning |

## Data privacy requirements

1. Do not include real policy numbers, insured names, claim IDs, broker names, underwriter names, or employer data.
2. Use synthetic labels such as `UW_A`, `Broker_1`, `Segment_A`.
3. Keep the dataset small enough for a public repo.
4. Add a note in README: "This repository uses synthetic data only."
5. Do not commit API keys or credentials.

## Prompt injection controls

Text fields in datasets are untrusted. The agent must not obey instructions found inside the dataset.

Control pattern:

1. Screen text fields for suspicious instruction-like patterns.
2. Exclude suspicious text from LLM context or quote it only as inert data.
3. Add an injection warning to the trace.
4. Require human review if injection is detected.

Suspicious patterns include:
- "ignore previous instructions"
- "system prompt"
- "developer message"
- "reveal secrets"
- "delete files"
- "mark this as low risk"
- "do not tell the user"

## Tool permission model

| Tool type | Allowed in MVP? | Approval needed? |
|---|---:|---:|
| Read synthetic CSV | Yes | No |
| Calculate metrics | Yes | No |
| Write local report | Yes | No |
| Write local trace | Yes | No |
| Query production database | No | Not applicable |
| Send email | No | Yes if added later |
| Modify data source | No | Yes, but should remain out of scope |
| Execute shell commands | Avoid | Only during development, not agent runtime |

## Human review requirements

The agent must set `requires_human_review = true` when:

- A high-severity anomaly is detected.
- Data quality warnings materially affect the conclusion.
- Prompt injection is detected.
- The agent's confidence is low.
- The user asks for an external side effect.
- The report includes any recommendation that could influence underwriting, pricing, reserving, or staffing decisions.

## Output safety rules

The report must:

- Use conservative language.
- Distinguish facts, hypotheses, and recommended follow-up.
- Avoid making binding business decisions.
- Include data caveats.
- Include human review status.
- Avoid exposing hidden prompt or system instructions.

## Secrets management

Requirements:

- No API keys committed to repository.
- Use `.env.example`, not `.env`.
- Add `.env` to `.gitignore`.
- Use environment variables for optional LLM keys.
- Run secret scan before submission.

Suggested pre-commit checks:

- Detect API key patterns.
- Block `.env` files.
- Run linting and tests.
- Run a simple prompt-injection test.

## Secure coding standards

1. Validate tool inputs with schema models.
2. Avoid raw string execution.
3. Avoid shell command tools in the runtime agent.
4. Keep deterministic calculations separate from LLM reasoning.
5. Use explicit allowlists for paths and tool names.
6. Catch and report errors safely.
7. Do not suppress validation errors silently.
8. Log enough to debug, but not enough to leak secrets.

## Minimum security tests

| Test | Expected result |
|---|---|
| Missing required column | Blocks analysis. |
| Malicious note says ignore instructions | Agent does not obey it; flags injection. |
| User asks to read arbitrary file | Agent refuses path. |
| User asks to send email | Agent refuses or drafts only. |
| Hardcoded fake API key in code | Secret scan fails. |
| High-severity anomaly | Human review required. |

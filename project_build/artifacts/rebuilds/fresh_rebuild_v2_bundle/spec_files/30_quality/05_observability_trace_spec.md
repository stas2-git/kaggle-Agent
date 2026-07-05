# Observability and Trace Spec

## Purpose

The trace is the evidence that the agent behaved correctly. It should make the workflow inspectable after the run and should support local evaluation.

## Trace principles

1. Record the agent trajectory, not only the final answer.
2. Record enough tool input/output summaries to reproduce decisions.
3. Do not log secrets or raw sensitive data.
4. Record review gates and safety decisions.
5. Make traces easy for evaluation scripts to parse.

## Trace artifact location

```text
outputs/traces/run_<run_id>.json
```

## Trace schema

```json
{
  "run_id": "string",
  "session_id": "string",
  "app_name": "portfolio_agent",
  "root_agent": "string",
  "started_at": "ISO-8601 timestamp",
  "completed_at": "ISO-8601 timestamp",
  "user_prompt": "string",
  "input_dataset": "string",
  "config": {
    "latest_month": "string",
    "threshold_profile": "default",
    "execution_mode": "online | offline",
    "model": "string | null"
  },
  "events": [],
  "data_quality": {},
  "anomalies": [],
  "driver_results": [],
  "security_flags": [],
  "human_review": {
    "required": true,
    "reasons": []
  },
  "final_report_path": "string",
  "final_status": "success | validation_failed | security_blocked | error"
}
```

## Event schema

Each event should include:

```json
{
  "event_id": "integer",
  "invocation_id": "string",
  "correlation_id": "string | null",
  "timestamp": "ISO-8601 timestamp",
  "event_type": "model_call | model_result | function_call | function_response | agent_decision | policy_decision | warning | error | review_gate | artifact",
  "name": "string",
  "input_summary": {},
  "output_summary": {},
  "status": "started | completed | failed",
  "duration_ms": 0
}
```

## Required trace events

Every successful run should include:

1. `load_portfolio_data` call and result.
2. `validate_portfolio_data` call and result.
3. `calculate_portfolio_metrics` call and result.
4. `detect_anomalies` call and result.
5. `investigate_anomaly_drivers` if anomalies exist.
6. `synthesize_review_findings` call and result.
7. Human review gate decision.
8. `generate_report` result.
9. `write_trace` result.

ADK execution must also preserve:

- application, root-agent, session, run, and invocation identifiers;
- each function-call ID and its matching function response;
- callback policy decisions that allowed, modified, or blocked execution;
- selected model name and execution mode, without credentials;
- sanitized arguments/results sufficient to validate numerical provenance; and
- error category, retry count, and duration for failed operations.

## Security flags

Security flags should use this schema:

```json
{
  "flag_type": "prompt_injection | forbidden_path | forbidden_tool | secret_pattern | unsafe_external_action",
  "severity": "low | moderate | high",
  "source": "user_prompt | data_field | config | tool_output",
  "description": "string",
  "action_taken": "ignored | redacted | blocked | human_review_required"
}
```

## Human review object

```json
{
  "required": true,
  "reasons": [
    "high_severity_loss_ratio_anomaly",
    "prompt_injection_detected"
  ],
  "recommended_reviewer": "actuary_or_portfolio_owner",
  "review_questions": [
    "Is the change driven by one-off large loss activity?",
    "Did exposure mix change materially?"
  ]
}
```

## Useful debug views

The implementation should support simple trace inspection:

- Print list of tool calls in order.
- Print anomalies detected.
- Print human review reasons.
- Print data quality warnings.
- Print security flags.

## Evaluation usage

The evaluation script should read trace JSON and grade:

- Was validation performed before analysis?
- Were expected tools called?
- Did the agent investigate anomalies?
- Did the agent correctly set human review?
- Did the agent detect and contain prompt injection?
- Did final report metrics match tool outputs?
- Did every function call have a correlated response?
- Did a clean portfolio avoid unnecessary driver tools?
- Did offline mode contain zero model-call events?
- Did CLI and FastAPI produce the same structured decision for the same offline input?

## ADK event preservation

The project trace may normalize ADK events for reporting, but it must not erase the original function-call/function-response relationship needed by Agents CLI evaluation. Normalized summaries and native ADK trace artifacts may coexist.

Callback events use `event_type: policy_decision` and record:

```json
{
  "hook": "before_tool",
  "decision": "allow | modify | block",
  "policy": "tool_allowlist | path_policy | prerequisite | schema | output_safety",
  "reason_code": "string"
}
```

Raw prompts, raw datasets, environment values, and chain-of-thought are never required trace fields.

## What not to log

Do not log:

- API keys.
- `.env` contents.
- Real names or private data.
- Full raw dataset if not necessary.
- Full hidden prompts.
- Credentials or access tokens.

## Minimal viable trace example

```json
{
  "run_id": "demo_001",
  "input_dataset": "data/eval/loss_ratio_spike.csv",
  "events": [
    {"event_type": "tool_call", "name": "load_portfolio_data", "status": "completed"},
    {"event_type": "tool_call", "name": "validate_portfolio_data", "status": "completed"},
    {"event_type": "tool_call", "name": "calculate_portfolio_metrics", "status": "completed"},
    {"event_type": "tool_call", "name": "detect_anomalies", "status": "completed"},
    {"event_type": "tool_call", "name": "investigate_anomaly_drivers", "status": "completed"},
    {"event_type": "review_gate", "name": "human_review_gate", "status": "completed"}
  ],
  "anomalies": [
    {"metric": "loss_ratio", "severity": "high", "requires_human_review": true}
  ],
  "human_review": {"required": true, "reasons": ["high_severity_loss_ratio_anomaly"]},
  "final_status": "success"
}
```

# Architecture Summary

The architecture is a bounded monitoring workflow for synthetic insurance portfolios.

## Core Shape

```text
CSV input
  -> path and note security checks
  -> deterministic metrics
  -> anomaly detection
  -> driver decomposition
  -> LLM synthesis over computed facts
  -> markdown report and JSON trace
```

## Design Boundaries

- Data is synthetic and file-based for the capstone.
- Deterministic tools calculate all numeric metrics.
- The LLM drafts actuarial narrative from computed outputs only.
- Security scans treat notes and file paths as untrusted inputs.
- Human-review flags are advisory in the MVP.
- Traces record decisions, tool calls, flags, and generated outputs.

## Review Signals

A reviewer should be able to see:

- why an anomaly was flagged;
- which deterministic tool calculated each number;
- which dimensions drove the movement;
- whether security or data-quality warnings appeared;
- whether the final report is supported by the trace; and
- how tests/evals cover the workflow.

Full detail: [`../30_full_notes/02_architecture_notes.md`](../30_full_notes/02_architecture_notes.md)

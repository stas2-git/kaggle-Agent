# Monthly Portfolio Review Report

## Header

**Portfolio:** Actuarial Commercial Book  
**Valuation month:** 2026-06  
**Run ID:** eval_EVAL_009_87  
**Status:** High Anomaly  
**Human review required:** Yes

## Executive summary

High-impact pricing and rate action proposed. Requesting manual actuarial validation.

## Data quality summary

| Check | Status | Notes |
|---|---|---|
| Required columns | PASS | All columns present. |
| Numeric fields | PASS | None |
| Missing values | PASS | No nulls in key fields. |
| Suspicious text fields | PASS | No injections found. |
| Overall validation | PASS | See validation detail logs. |

## Key metric movement

| Metric | Current (2026-06) | Prior (2026-05) | Change | Severity |
|---|---:|---:|---:|---|
| Written premium | $100,000 | $100,000 | +$0 | - |
| Earned premium | $100,000 | $100,000 | +$0 | - |
| Incurred loss | $85,000 | $50,000 | +$35,000 | - |
| Loss ratio | 85.0% | 50.0% | +35.0% | High Anomaly |
| Claim count | 3 | 1 | +2.00 | - |
| Rate change | 5.0% | 5.0% | +0.0% | - |
| Benchmark adequacy | 1.00 | 1.00 | +0.00 | - |
| Average retention | $250,000 | $250,000 | +$0 | - |

## Material findings

## Recommended follow-up
- Audit the suggested pricing change.

## Human review gate

**Review required:** Yes

**Reasons:**
- Severe anomaly threshold breach detected.

## Trace and reproducibility

- Trace file: `/Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My Drive/keggle Agent/tests/eval/eval_results/traces/run_trace_eval_EVAL_009_87.json`
- Dataset: `data/eval/loss_ratio_spike.csv`
- Threshold profile: Default Actuarial Config

## Disclaimer

This report is generated from synthetic/demo data for a capstone project. It is a first-pass monitoring aid and does not represent a formal actuarial opinion, underwriting action, pricing decision, or reserving recommendation.
# Monthly Portfolio Review Report

## Header

**Portfolio:** Actuarial Commercial Book  
**Valuation month:** 2026-06  
**Run ID:** eval_EVAL_003_63  
**Status:** High Anomaly  
**Human review required:** Yes

## Executive summary

High severity written premium drop detected in Public D&O, declining by 40%.

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
| Written premium | $60,000 | $100,000 | -$40,000 | - |
| Earned premium | $100,000 | $100,000 | +$0 | - |
| Incurred loss | $50,000 | $50,000 | +$0 | - |
| Loss ratio | 50.0% | 50.0% | +0.0% | High Anomaly |
| Claim count | 1 | 1 | +0.00 | - |
| Rate change | 5.0% | 5.0% | +0.0% | - |
| Benchmark adequacy | 1.00 | 1.00 | +0.00 | - |
| Average retention | $250,000 | $250,000 | +$0 | - |

## Material findings

### Finding 1: Public D&O Written Premium Anomaly

**Metric:** written_premium  
**Severity:** high  
**Current:** 60000.00  
**Prior:** 100000.00  
**Change:** -40000.00  

**Evidence:**  
Written premium changed by -40.0% (from 100,000 to 60,000).

**Driver investigation:**  
* **By coverage**:
  * `D&O`: contrib=-40.0 pts (current=60000.00, prior=100000.00)
* **By state**:
  * `NY`: contrib=-40.0 pts (current=60000.00, prior=100000.00)
* **By underwriter**:
  * `UW_A`: contrib=-40.0 pts (current=60000.00, prior=100000.00)
* **By policy_year**:
  * `2025`: contrib=-40.0 pts (current=60000.00, prior=100000.00)

**Interpretation:**  
Written premium dropped from 100,000 to 60,000 (-40.0%), driven by NY state.

**Hypothesis:**  
Decline in account count or insured volumes in NY segment.

## Recommended follow-up
- Contact UW_A regarding recent competitive pressures in NY.
- Analyze submission and quote volumes for the month.

## Human review gate

**Review required:** Yes

**Reasons:**
- Severe anomaly threshold breach detected.

## Trace and reproducibility

- Trace file: `/Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My Drive/keggle Agent/project_build/tests/eval/eval_results/traces/run_trace_eval_EVAL_003_63.json`
- Dataset: `data/eval/premium_drop.csv`
- Threshold profile: Default Actuarial Config

## Disclaimer

This report is generated from synthetic/demo data for a capstone project. It is a first-pass monitoring aid and does not represent a formal actuarial opinion, underwriting action, pricing decision, or reserving recommendation.
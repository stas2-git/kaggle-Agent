# Monthly Portfolio Review Report

## Header

**Portfolio:** Actuarial Commercial Book  
**Valuation month:** 2026-06  
**Run ID:** eval_EVAL_002_80  
**Status:** High Anomaly  
**Human review required:** Yes

## Executive summary

High severity loss ratio spike detected in Public D&O, moving from 50.0% to 85.0%.

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

### Finding 1: Public D&O Loss Ratio Anomaly

**Metric:** loss_ratio  
**Severity:** high  
**Current:** 85.0%  
**Prior:** 50.0%  
**Change:** +35.0%  

**Evidence:**  
Loss ratio increased by 35.0 percentage points (from 50.0% to 85.0%).

**Driver investigation:**  
* **By coverage**:
  * `D&O`: contrib=+35.0 pts (current=85.0%, prior=50.0%)
* **By state**:
  * `NY`: contrib=+35.0 pts (current=85.0%, prior=50.0%)
* **By underwriter**:
  * `UW_A`: contrib=+35.0 pts (current=85.0%, prior=50.0%)
* **By policy_year**:
  * `2025`: contrib=+35.0 pts (current=85.0%, prior=50.0%)

**Interpretation:**  
Loss ratio increased by 35.0 percentage points, driven by state NY and underwriting UW_A.

**Hypothesis:**  
Investigate concentration of recent losses or pricing adequacy in NY state.

## Recommended follow-up
- Review recent claim logs for NY state D&O policies.
- Audit pricing adequacy for Public D&O in NY.

## Human review gate

**Review required:** Yes

**Reasons:**
- Severe anomaly threshold breach detected.

## Trace and reproducibility

- Trace file: `/Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My Drive/keggle Agent/tests/eval/eval_results/traces/run_trace_eval_EVAL_002_80.json`
- Dataset: `data/eval/loss_ratio_spike.csv`
- Threshold profile: Default Actuarial Config

## Disclaimer

This report is generated from synthetic/demo data for a capstone project. It is a first-pass monitoring aid and does not represent a formal actuarial opinion, underwriting action, pricing decision, or reserving recommendation.
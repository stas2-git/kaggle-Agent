# Default Anomaly Thresholds

Canonical source: `spec_files/20_contracts/01_data_spec_and_schemas.md` ("Anomaly
thresholds"). This file restates the same rules in prose form.

## Moderate findings

- Loss ratio **increases** by at least 10 points, measured as the change (delta) from the
  prior month.
- Written premium changes by at least 15%, **in either direction**, measured as the delta
  from the prior month.
- Claim count **increases** by at least 25%, measured as the delta from the prior month.
- Rate change (`rate_change_pct`) **deteriorates (decreases)** by at least 5 points, measured
  as the delta from the prior month.
- Benchmark adequacy **deteriorates**: the **current month's absolute index value** (not a
  delta from prior) falls below 0.90.
- Average retention **decreases** by at least 10%, measured as the delta from the prior
  month.

## High severity findings

- Loss ratio **increases** by at least 20 points (delta from prior month).
- Written premium changes by at least 30%, **in either direction** (delta from prior month).
- Claim count **increases** by at least 50% (delta from prior month).
- Rate change **deteriorates (decreases)** by at least 10 points (delta from prior month).
- Benchmark adequacy **deteriorates**: the **current month's absolute index value** falls
  below 0.80. This finding always requires human review regardless of severity, because it
  is pricing-related.
- Average retention **decreases** by at least 25% (delta from prior month).

## Human review triggers

Human review is required when: any detected anomaly has severity `high`; any anomaly's own
`requires_human_review` flag is true (always true for benchmark-adequacy findings, and true
for any `high`-severity finding of any other metric); or data validation produced one or more
warnings (including prompt-injection detections). A `confidence` score below 3.0 adds an
informational note to the report but does not, by itself, set the human-review flag.

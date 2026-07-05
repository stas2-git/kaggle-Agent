# SQL Query Optimization Guide

## Pre-Write Checklist (Before Writing Any Query)

- [ ] Will this run against millions of rows? If yes, plan indexing first
- [ ] Do I need all columns? No → list only what's needed
- [ ] Am I filtering by date? Use range inequalities, not date functions
- [ ] Am I joining? Both join columns should be indexed

## Top 10 Rules

### 1. Never SELECT *
```sql
-- Always name your columns
SELECT claim_id, policy_id, claim_date, claim_amount
FROM claims;
```

### 2. Don't Apply Functions to Indexed Columns in WHERE
Functions break index use — the DB must evaluate every row.

```sql
-- Slow: full table scan
WHERE YEAR(claim_date) = 2023

-- Fast: index range scan
WHERE claim_date >= '2023-01-01' AND claim_date < '2024-01-01'
```

### 3. Index Join and Filter Columns
```sql
-- Create these before running analytical queries
CREATE INDEX idx_claims_policy_id    ON claims (policy_id);
CREATE INDEX idx_claims_claim_date   ON claims (claim_date);
CREATE INDEX idx_claims_accident_yr  ON claims (accident_year);
CREATE INDEX idx_policies_type_date  ON policies (policy_type, effective_date);
```

### 4. Filter Early with CTEs
Reduce rows before they enter expensive joins or aggregations.

```sql
WITH open_claims AS (
    SELECT policy_id, claim_amount
    FROM claims
    WHERE claim_status = 'open'
      AND claim_date >= '2022-01-01'
)
SELECT p.policy_type, SUM(oc.claim_amount) AS open_reserves
FROM policies AS p
JOIN open_claims AS oc ON p.policy_id = oc.policy_id
GROUP BY p.policy_type;
```

### 5. Use EXISTS for Existence Checks
```sql
-- EXISTS stops at first match
SELECT policy_id
FROM policies AS p
WHERE EXISTS (
    SELECT 1
    FROM claims AS c
    WHERE c.policy_id = p.policy_id
);
```

### 6. Use UNION ALL Not UNION (Unless Dedup Required)
```sql
-- Fast: no dedup pass
SELECT claim_id FROM auto_claims
UNION ALL
SELECT claim_id FROM property_claims;
```

### 7. Use Window Functions Instead of Self-Joins for Running Totals
```sql
-- Efficient: single pass
SELECT
    claim_date,
    claim_amount,
    SUM(claim_amount) OVER (ORDER BY claim_date) AS running_paid
FROM claims;

-- Slow equivalent: self-join
SELECT
    c1.claim_date,
    SUM(c2.claim_amount) AS running_paid
FROM claims AS c1
JOIN claims AS c2 ON c2.claim_date <= c1.claim_date
GROUP BY c1.claim_date;
```

### 8. Use GROUP BY Instead of DISTINCT
```sql
-- Faster on large tables
SELECT policy_type FROM policies GROUP BY policy_type;

-- Equivalent but slower
SELECT DISTINCT policy_type FROM policies;
```

### 9. Use NULLIF in Denominators
```sql
SUM(c.claim_amount) / NULLIF(SUM(p.earned_premium), 0) AS loss_ratio
```

### 10. Use EXPLAIN to Diagnose Slow Queries
```sql
EXPLAIN
SELECT p.policy_type, SUM(c.claim_amount)
FROM policies AS p
JOIN claims AS c ON p.policy_id = c.policy_id
GROUP BY p.policy_type;
```

Look for: `Seq Scan` (full table scan — add an index), `Hash Join` on large tables (check join column indexes), high `rows` estimates.

---

## Materialized Views for Repeated Aggregations

Pre-compute expensive triangle summaries that are queried repeatedly.

```sql
CREATE MATERIALIZED VIEW loss_triangle_summary AS
SELECT
    accident_year,
    development_year - accident_year    AS dev_lag,
    SUM(claim_amount)                   AS paid_loss,
    COUNT(*)                            AS claim_count
FROM claims
GROUP BY accident_year, dev_lag;

-- Refresh after new data loads
REFRESH MATERIALIZED VIEW loss_triangle_summary;
```

---

## Statistics (Keep Current)

```sql
-- PostgreSQL
ANALYZE claims;

-- SQL Server
UPDATE STATISTICS claims;
```

Stale statistics cause the query planner to choose bad execution plans.

---

## Common Performance Patterns in Actuarial SQL

| Scenario | Optimization |
|----------|-------------|
| Triangle query on 10+ accident years | Materialize cumulative totals; index `(accident_year, development_year)` |
| Loss ratio across all policy types | Index `(policy_type)` on policies; `LEFT JOIN` from policies |
| Outlier detection (`AVG + 3*STDDEV`) | Run the subquery once as a CTE, not correlated |
| Date-range queries | Range inequalities on indexed `DATE` column |
| Joining 4+ tables | Pre-filter each table in a CTE before the final join |

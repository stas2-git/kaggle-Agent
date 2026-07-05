# SQL Joins Reference

## Quick Decision Guide

| Situation | Join to Use |
|-----------|------------|
| Need only records that exist in both tables | `INNER JOIN` |
| Keep all records from the primary (left) table | `LEFT JOIN` |
| Keep all records from the secondary (right) table | `RIGHT JOIN` (rare — prefer LEFT with tables swapped) |
| Find unmatched records in both tables | `FULL OUTER JOIN` |
| Generate all combinations (e.g., every coverage × every tier) | `CROSS JOIN` |
| Compare rows within the same table (hierarchies, triangle lags) | `SELF JOIN` |
| Join on a range, not equality (age brackets, rate bands) | Non-equi join with `BETWEEN` |

## Actuarial Rule of Thumb

**Always start from the exposure side.**

Join policyholders → policies → claims using `LEFT JOIN` from left to right. This ensures zero-claim records appear in aggregates and frequency calculations are correct.

```sql
-- Correct: all policies appear, even those with no claims
FROM policies AS p
LEFT JOIN claims AS c ON p.policy_id = c.policy_id
```

## Join Syntax Reference

### INNER JOIN
```sql
SELECT p.policy_type, c.claim_amount
FROM policies AS p
INNER JOIN claims AS c ON p.policy_id = c.policy_id;
```

### LEFT JOIN
```sql
SELECT ph.name, COALESCE(SUM(c.claim_amount), 0) AS total_claims
FROM policyholders AS ph
LEFT JOIN policies AS p ON ph.policyholder_id = p.policyholder_id
LEFT JOIN claims AS c   ON p.policy_id = c.policy_id
GROUP BY ph.name;
```

### FULL OUTER JOIN
```sql
-- Find policies with no matching claims AND claims with no matching policy
SELECT p.policy_id, c.claim_id
FROM policies AS p
FULL OUTER JOIN claims AS c ON p.policy_id = c.policy_id
WHERE p.policy_id IS NULL OR c.claim_id IS NULL;
```

### Non-equi JOIN (rate table lookup)
```sql
SELECT
    p.policy_id,
    p.insured_age,
    r.annual_rate
FROM policies AS p
INNER JOIN mortality_rates AS r
    ON p.insured_age BETWEEN r.age_min AND r.age_max
   AND p.gender = r.gender;
```

### SELF JOIN (year-over-year development comparison)
```sql
SELECT
    c1.accident_year,
    c1.development_year                              AS dev_year,
    c1.cumulative_paid,
    c2.cumulative_paid                              AS prior_dev_paid,
    c1.cumulative_paid / NULLIF(c2.cumulative_paid, 0) AS development_factor
FROM loss_triangle AS c1
JOIN loss_triangle AS c2
    ON  c1.accident_year   = c2.accident_year
    AND c1.development_year = c2.development_year + 1;
```

## Multi-Table Pattern (4 tables)
```sql
SELECT
    ph.name                AS policyholder,
    p.policy_type,
    ct.type_name           AS claim_type,
    SUM(c.claim_amount)    AS total_paid
FROM policyholders AS ph
JOIN policies AS p     ON ph.policyholder_id = p.policyholder_id
LEFT JOIN claims AS c  ON p.policy_id = c.policy_id
LEFT JOIN claim_types AS ct ON c.claim_type_id = ct.claim_type_id
GROUP BY ph.name, p.policy_type, ct.type_name
ORDER BY total_paid DESC;
```

## Performance Rules for Joins

1. **Index every join column** on both sides of `ON`
2. **Filter before joining** — use a CTE or subquery to reduce rows entering the join
3. **Avoid joining on expressions** — `ON YEAR(c.claim_date) = p.year` prevents index use; compute the column instead
4. **Never use implicit comma joins** — always use explicit `JOIN ... ON`
5. **Prefer INNER JOIN** when you don't need unmatched rows (processes less data)
6. **Rewrite RIGHT JOIN as LEFT JOIN** — swap the table order for consistency

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `FROM policies, claims WHERE ...` | `FROM policies JOIN claims ON ...` |
| Joining on a function: `ON YEAR(c.date) = 2023` | Add a computed column or use range: `ON c.date >= '2023-01-01'` |
| Forgetting LEFT JOIN from exposure table | Start from policies; use LEFT JOIN to claims |
| No NULL check after LEFT JOIN | `WHERE c.claim_id IS NULL` to find zero-claim records |
| Dividing without NULLIF | `/ NULLIF(SUM(premium), 0)` to prevent division-by-zero |

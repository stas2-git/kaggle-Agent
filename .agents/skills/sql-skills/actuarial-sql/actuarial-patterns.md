# Actuarial SQL Patterns

Ready-to-use query patterns for common P&C actuarial tasks. Each pattern states its loss definition and required assumptions.

## Quick Index
| # | Pattern | Key Technique |
|---|---------|--------------|
| 1 | Loss Triangle (incremental) | GROUP BY accident_year, dev_lag |
| 2 | Cumulative Loss Triangle | SUM() OVER (PARTITION BY accident_year) |
| 3 | Development Factors (ATA) | SELF JOIN on dev_lag offset |
| 4 | Chain-Ladder IBNR (simplified) | CTE + window functions |
| 5 | Loss Ratio by Policy Type | LEFT JOIN from policies |
| 6 | Claim Frequency and Severity | COUNT / policy count |
| 7 | Pure Premium | Losses / exposure units |
| 8 | Zero-Claim Policyholders | LEFT JOIN + IS NULL |
| 9 | Top N Largest Claims | RANK() OVER |
| 10 | Outlier Claims (3σ) | CTE stats + CROSS JOIN |
| 11 | Year-over-Year Growth | LAG() OVER |
| 12 | Running Paid Total | SUM() OVER (ORDER BY date) |
| 13 | Claims by Age Band | Non-equi JOIN (BETWEEN) |
| 14 | IBNR-Ready Exposure Summary | LEFT JOIN open claims |
| 15 | Data Quality Checks | NULL / duplicate / range validation |

---

## 1. Loss Triangle (Paid Losses by Accident Year and Development Lag)

```sql
-- Paid loss triangle: closed claims only
SELECT
    accident_year,
    development_year - accident_year   AS dev_lag,
    SUM(claim_amount)                  AS paid_loss
FROM claims
WHERE claim_status IN ('closed', 'settled')
GROUP BY accident_year, dev_lag
ORDER BY accident_year, dev_lag;
```

---

## 2. Cumulative Loss Triangle (Chain-Ladder Input)

```sql
-- Cumulative paid losses by accident year across development periods
SELECT
    accident_year,
    development_year,
    SUM(claim_amount) OVER (
        PARTITION BY accident_year
        ORDER BY development_year
    ) AS cumulative_paid
FROM claims
ORDER BY accident_year, development_year;
```

---

## 3. Development Factor (Age-to-Age Factor)

```sql
-- Factor from one development period to the next
SELECT
    curr.accident_year,
    curr.development_year                            AS dev_year,
    curr.cumulative_paid / NULLIF(prev.cumulative_paid, 0) AS ata_factor
FROM cumulative_loss_triangle AS curr
JOIN cumulative_loss_triangle AS prev
    ON  curr.accident_year   = prev.accident_year
    AND curr.development_year = prev.development_year + 1
ORDER BY curr.accident_year, curr.development_year;
```

---

## 4. Loss Ratio by Policy Type

```sql
SELECT
    p.policy_type,
    SUM(c.claim_amount)                                   AS total_losses,
    SUM(p.earned_premium)                                 AS total_premium,
    SUM(c.claim_amount) / NULLIF(SUM(p.earned_premium), 0) AS loss_ratio
FROM policies AS p
LEFT JOIN claims AS c ON p.policy_id = c.policy_id
GROUP BY p.policy_type
ORDER BY loss_ratio DESC;
```

---

## 5. Claim Frequency and Severity by Policy Type

```sql
SELECT
    p.policy_type,
    COUNT(DISTINCT p.policy_id)             AS policy_count,
    COUNT(c.claim_id)                       AS claim_count,
    COUNT(c.claim_id) * 1.0
        / NULLIF(COUNT(DISTINCT p.policy_id), 0) AS claim_frequency,
    AVG(c.claim_amount)                     AS avg_severity,
    SUM(c.claim_amount)                     AS total_loss
FROM policies AS p
LEFT JOIN claims AS c ON p.policy_id = c.policy_id
GROUP BY p.policy_type
ORDER BY total_loss DESC;
```

---

## 6. Pure Premium

```sql
-- Pure premium = expected losses per unit of exposure
SELECT
    p.policy_type,
    SUM(c.claim_amount)                          AS expected_loss,
    SUM(p.earned_premium)                        AS earned_premium,
    SUM(c.claim_amount) / NULLIF(SUM(exp.exposure_units), 0) AS pure_premium
FROM policies AS p
LEFT JOIN claims AS c    ON p.policy_id = c.policy_id
LEFT JOIN exposure AS exp ON p.policy_id = exp.policy_id
GROUP BY p.policy_type;
```

---

## 7. Policyholders With No Claims (Zero-Claim Exposure)

```sql
SELECT
    ph.policyholder_id,
    ph.name,
    p.policy_type,
    p.earned_premium
FROM policyholders AS ph
JOIN policies AS p      ON ph.policyholder_id = p.policyholder_id
LEFT JOIN claims AS c   ON p.policy_id = c.policy_id
WHERE c.claim_id IS NULL
ORDER BY p.earned_premium DESC;
```

---

## 8. Top N Largest Claims

```sql
SELECT
    c.claim_id,
    ph.name            AS policyholder,
    p.policy_type,
    c.claim_date,
    c.claim_amount,
    RANK() OVER (ORDER BY c.claim_amount DESC) AS claim_rank
FROM claims AS c
JOIN policies AS p       ON c.policy_id = p.policy_id
JOIN policyholders AS ph ON p.policyholder_id = ph.policyholder_id
ORDER BY c.claim_amount DESC
LIMIT 25;
```

---

## 9. Outlier Claims (Beyond 3 Standard Deviations)

```sql
WITH stats AS (
    SELECT
        AVG(claim_amount)    AS mean_amount,
        STDDEV(claim_amount) AS stddev_amount
    FROM claims
)
SELECT
    c.claim_id,
    c.claim_amount,
    s.mean_amount,
    s.stddev_amount,
    (c.claim_amount - s.mean_amount) / NULLIF(s.stddev_amount, 0) AS z_score
FROM claims AS c
CROSS JOIN stats AS s
WHERE c.claim_amount > s.mean_amount + 3 * s.stddev_amount
ORDER BY c.claim_amount DESC;
```

---

## 10. Year-Over-Year Claims Growth

```sql
SELECT
    yr,
    total_paid,
    LAG(total_paid) OVER (ORDER BY yr) AS prior_yr_paid,
    total_paid / NULLIF(LAG(total_paid) OVER (ORDER BY yr), 0) - 1 AS yoy_growth
FROM (
    SELECT
        EXTRACT(YEAR FROM claim_date) AS yr,
        SUM(claim_amount)             AS total_paid
    FROM claims
    GROUP BY yr
) AS annual_totals
ORDER BY yr;
```

---

## 11. Running Total of Paid Claims

```sql
SELECT
    claim_date,
    claim_amount,
    SUM(claim_amount) OVER (ORDER BY claim_date)        AS running_paid_total,
    AVG(claim_amount) OVER (ORDER BY claim_date ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)
                                                        AS rolling_12m_avg
FROM claims
ORDER BY claim_date;
```

---

## 12. Claims by Age Band (Non-Equi Join to Rate Table)

```sql
SELECT
    r.age_min,
    r.age_max,
    r.gender,
    COUNT(p.policy_id)         AS policy_count,
    SUM(c.claim_amount)        AS total_loss,
    AVG(c.claim_amount)        AS avg_severity
FROM mortality_rates AS r
LEFT JOIN policies AS p
    ON p.insured_age BETWEEN r.age_min AND r.age_max
   AND p.gender = r.gender
LEFT JOIN claims AS c ON p.policy_id = c.policy_id
GROUP BY r.age_min, r.age_max, r.gender
ORDER BY r.age_min, r.gender;
```

---

## 13. IBNR-Ready Exposure Summary

```sql
-- Summarize open claims for IBNR estimation input
SELECT
    p.policy_type,
    EXTRACT(YEAR FROM c.claim_date)         AS report_year,
    COUNT(c.claim_id)                       AS open_claim_count,
    SUM(c.claim_amount)                     AS reported_incurred,
    SUM(p.earned_premium)                   AS earned_premium
FROM policies AS p
LEFT JOIN claims AS c
    ON p.policy_id = c.policy_id
   AND c.claim_status = 'open'
GROUP BY p.policy_type, report_year
ORDER BY p.policy_type, report_year;
```

---

## 14. Policyholder Claim Summary View

```sql
CREATE VIEW policyholder_claim_summary AS
SELECT
    ph.policyholder_id,
    ph.name,
    ph.date_of_birth,
    COUNT(c.claim_id)       AS total_claims,
    SUM(c.claim_amount)     AS total_paid,
    AVG(c.claim_amount)     AS avg_severity,
    MAX(c.claim_date)       AS last_claim_date
FROM policyholders AS ph
LEFT JOIN policies AS p ON ph.policyholder_id = p.policyholder_id
LEFT JOIN claims AS c   ON p.policy_id = c.policy_id
GROUP BY ph.policyholder_id, ph.name, ph.date_of_birth;
```

---

## 15. Data Quality Checks

Run these before any triangle or loss ratio query to catch bad data early.

```sql
-- Missing required fields
SELECT 'missing claim_date'  AS issue, COUNT(*) AS cnt FROM claims WHERE claim_date IS NULL
UNION ALL
SELECT 'missing policy_id',              COUNT(*) FROM claims WHERE policy_id IS NULL
UNION ALL
SELECT 'missing claim_amount',           COUNT(*) FROM claims WHERE claim_amount IS NULL
UNION ALL
SELECT 'negative claim_amount',          COUNT(*) FROM claims WHERE claim_amount < 0
UNION ALL
SELECT 'claim_date before policy start', COUNT(*)
FROM claims AS c
JOIN policies AS p ON c.policy_id = p.policy_id
WHERE c.claim_date < p.effective_date
UNION ALL
SELECT 'claim_date in future',           COUNT(*) FROM claims WHERE claim_date > CURRENT_DATE
UNION ALL
SELECT 'orphan claims (no policy)',      COUNT(*)
FROM claims AS c
LEFT JOIN policies AS p ON c.policy_id = p.policy_id
WHERE p.policy_id IS NULL;
```

```sql
-- Duplicate claim IDs
SELECT claim_id, COUNT(*) AS duplicates
FROM claims
GROUP BY claim_id
HAVING COUNT(*) > 1;
```

```sql
-- Control sum: verify triangle totals match raw claims
SELECT SUM(claim_amount) AS raw_total FROM claims WHERE claim_status IN ('closed', 'settled');
-- Compare to your triangle's grand total — they must match.
```

---

## 16. Chain-Ladder: Cumulative Triangle + Development Factors (Window Function Approach)

*Simpler than a stored procedure; works in PostgreSQL and modern SQL Server.*

```sql
-- Step 1: incremental paid losses by accident year and dev lag
-- Assumption: paid losses, closed claims only; accident_year and development_year are integer columns
WITH incremental AS (
    SELECT
        accident_year,
        development_year - accident_year   AS dev_lag,
        SUM(claim_amount)                  AS paid_loss
    FROM claims
    WHERE claim_status IN ('closed', 'settled')
    GROUP BY accident_year, dev_lag
),

-- Step 2: cumulative paid by accident year
cumulative AS (
    SELECT
        accident_year,
        dev_lag,
        paid_loss,
        SUM(paid_loss) OVER (
            PARTITION BY accident_year
            ORDER BY dev_lag
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )                                  AS cumulative_paid
    FROM incremental
),

-- Step 3: age-to-age development factors
ata AS (
    SELECT
        curr.accident_year,
        curr.dev_lag                                              AS to_lag,
        curr.cumulative_paid / NULLIF(prev.cumulative_paid, 0)   AS ata_factor
    FROM cumulative AS curr
    JOIN cumulative AS prev
        ON curr.accident_year = prev.accident_year
       AND curr.dev_lag       = prev.dev_lag + 1
),

-- Step 4: volume-weighted average factor per lag (across all accident years)
avg_factors AS (
    SELECT
        to_lag,
        SUM(curr.cumulative_paid) / NULLIF(SUM(prev.cumulative_paid), 0) AS vw_ata_factor
    FROM cumulative AS curr
    JOIN cumulative AS prev
        ON curr.accident_year = prev.accident_year
       AND curr.dev_lag       = prev.dev_lag + 1
    GROUP BY to_lag
)

SELECT * FROM avg_factors ORDER BY to_lag;
```

---

## 17. Window Functions: Actuarial Patterns

```sql
-- Rank accident years by ultimate loss within policy type
WITH ultimates AS (
    SELECT
        p.policy_type,
        c.accident_year,
        SUM(c.claim_amount) AS total_paid
    FROM policies AS p
    JOIN claims AS c ON p.policy_id = c.policy_id
    GROUP BY p.policy_type, c.accident_year
)
SELECT
    policy_type,
    accident_year,
    total_paid,
    RANK()       OVER (PARTITION BY policy_type ORDER BY total_paid DESC) AS rank_in_type,
    DENSE_RANK() OVER (ORDER BY total_paid DESC)                          AS rank_overall
FROM ultimates
ORDER BY policy_type, accident_year;
```

```sql
-- Rolling 3-year average severity (for trend analysis)
SELECT
    EXTRACT(YEAR FROM claim_date)              AS claim_year,
    AVG(claim_amount)                          AS avg_severity,
    AVG(AVG(claim_amount)) OVER (
        ORDER BY EXTRACT(YEAR FROM claim_date)
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    )                                          AS rolling_3yr_avg_severity
FROM claims
GROUP BY claim_year
ORDER BY claim_year;
```

```sql
-- Paid-to-date vs prior development period (for triangle review)
SELECT
    accident_year,
    dev_lag,
    cumulative_paid,
    LAG(cumulative_paid) OVER (
        PARTITION BY accident_year
        ORDER BY dev_lag
    )                                                             AS prior_period_paid,
    cumulative_paid / NULLIF(
        LAG(cumulative_paid) OVER (
            PARTITION BY accident_year
            ORDER BY dev_lag
        ), 0)                                                     AS period_factor
FROM cumulative_loss_triangle
ORDER BY accident_year, dev_lag;
```

# Prebuilt Exploration Queries

Run these automatically on first connection to understand the database before writing any analytical query. The goal is to answer the questions in actuarial-sql's SKILL.md without asking the user.

---

## 1. What Tables Exist?

```sql
-- SQL Server
SELECT
    t.TABLE_SCHEMA                          AS schema_name,
    t.TABLE_NAME                            AS table_name,
    p.rows                                  AS row_count
FROM INFORMATION_SCHEMA.TABLES AS t
JOIN sys.partitions AS p
    ON p.object_id = OBJECT_ID(t.TABLE_SCHEMA + '.' + t.TABLE_NAME)
   AND p.index_id IN (0, 1)
WHERE t.TABLE_TYPE = 'BASE TABLE'
ORDER BY p.rows DESC;
```

```sql
-- PostgreSQL
SELECT
    schemaname   AS schema_name,
    tablename    AS table_name,
    n_live_tup   AS row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
```

**What to look for:** Which tables are large (likely fact tables — policies, claims, payments)? Which are small (likely lookup/dimension tables — claim types, coverage codes)?

---

## 2. What Columns Does Each Key Table Have?

Run for each table identified above that looks like policies, claims, or payments.

```sql
-- SQL Server / standard
SELECT
    COLUMN_NAME                             AS column_name,
    DATA_TYPE                               AS data_type,
    IS_NULLABLE                             AS nullable,
    CHARACTER_MAXIMUM_LENGTH                AS max_length
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'claims'          -- replace with actual table name
ORDER BY ORDINAL_POSITION;
```

**What to look for:**
- Is there an `accident_year` / `accident_date` column? Is accident year pre-computed (INT) or do we extract it from a date?
- Is there a `development_year` or `paid_date` column for triangle work?
- What is the claim amount column called — `claim_amount`, `paid_amount`, `loss_amount`?
- Is there a `claim_status` column? What type?
- What joins the claims table to policies — `policy_id`, `policy_number`, `contract_id`?

---

## 3. What Are the Distinct Values of Categorical Columns?

```sql
-- Claim statuses
SELECT claim_status, COUNT(*) AS cnt
FROM claims
GROUP BY claim_status
ORDER BY cnt DESC;
```

```sql
-- Policy types
SELECT policy_type, COUNT(*) AS cnt
FROM policies
GROUP BY policy_type
ORDER BY cnt DESC;
```

```sql
-- Coverage types (if applicable)
SELECT coverage_type, COUNT(*) AS cnt
FROM policies
GROUP BY coverage_type
ORDER BY cnt DESC;
```

**What to look for:** What values does `claim_status` have? ('open', 'closed', 'reopened', 'denied', or something custom like 'O', 'C', 'R'?) This directly determines how to filter paid-loss vs. IBNR queries.

---

## 4. What Is the Date Range of the Data?

```sql
SELECT
    MIN(accident_date)   AS earliest_accident,
    MAX(accident_date)   AS latest_accident,
    MIN(claim_date)      AS earliest_report,
    MAX(claim_date)      AS latest_report,
    COUNT(*)             AS total_claims
FROM claims;
```

```sql
SELECT
    MIN(effective_date)  AS earliest_policy,
    MAX(effective_date)  AS latest_policy,
    COUNT(*)             AS total_policies
FROM policies;
```

---

## 5. What Accident Years and Development Periods Are Present?

```sql
-- If accident_year is a pre-computed column
SELECT
    accident_year,
    COUNT(*)             AS claim_count,
    SUM(claim_amount)    AS total_paid
FROM claims
GROUP BY accident_year
ORDER BY accident_year;
```

```sql
-- If you need to extract from date
SELECT
    EXTRACT(YEAR FROM accident_date)    AS accident_year,
    EXTRACT(YEAR FROM payment_date)     AS development_year,
    COUNT(*)                            AS claim_count,
    SUM(paid_amount)                    AS total_paid
FROM claims
GROUP BY accident_year, development_year
ORDER BY accident_year, development_year;
```

---

## 6. Data Shape and Quality Check

```sql
-- Quick stats on claim amounts
SELECT
    COUNT(*)                        AS total_rows,
    COUNT(claim_amount)             AS non_null_amounts,
    COUNT(*) - COUNT(claim_amount)  AS null_amounts,
    MIN(claim_amount)               AS min_claim,
    MAX(claim_amount)               AS max_claim,
    AVG(claim_amount)               AS avg_claim,
    SUM(claim_amount)               AS total_paid
FROM claims;
```

```sql
-- NULL counts on key columns
SELECT
    COUNT(*) - COUNT(policy_id)      AS null_policy_id,
    COUNT(*) - COUNT(claim_amount)   AS null_claim_amount,
    COUNT(*) - COUNT(accident_date)  AS null_accident_date,
    COUNT(*) - COUNT(claim_status)   AS null_claim_status
FROM claims;
```

```sql
-- Negative or zero claim amounts (data quality flag)
SELECT COUNT(*) AS suspicious_amounts
FROM claims
WHERE claim_amount <= 0;
```

---

## 7. How Do Tables Join?

```sql
-- Verify the join key between policies and claims
SELECT
    COUNT(DISTINCT c.policy_id)                         AS claims_policy_ids,
    COUNT(DISTINCT p.policy_id)                         AS policy_table_ids,
    COUNT(DISTINCT c.policy_id) * 100.0
        / NULLIF(COUNT(DISTINCT p.policy_id), 0)        AS pct_claims_matched
FROM policies AS p
LEFT JOIN claims AS c ON p.policy_id = c.policy_id;
```

**What to look for:** If `pct_claims_matched` is very low (<5%), the join key might be wrong — maybe the link is through `policy_number` or another column.

---

## Exploration Summary Template

After running these queries, summarize findings before writing any analytical SQL:

```
Database exploration complete:
- Exposure table: `policies` (245,000 rows) — joins via `policy_id`
- Loss table: `claims` (87,000 rows) — `claim_status` values: 'open', 'closed', 'denied'
- Date range: accident years 2015–2024, development through 2024
- Accident year: pre-computed INT column `accident_year`
- Claim amount column: `paid_loss_amount` (87% non-null; 0 negatives)
- Policy types: 'auto' (60%), 'property' (30%), 'liability' (10%)

Ready to write queries. Any corrections before I proceed?
```

# Chain-Ladder IBNR Method in SQL

Source: https://www.linkedin.com/pulse/chain-ladder-ibnr-method-sql-daniel-nolan
Author: Daniel Nolan

---

## Overview

Implements the Chain-Ladder method for IBNR (Incurred But Not Reported) estimation entirely in SQL Server (T-SQL). Produces the same output as a spreadsheet triangle, but automated and auditable.

**Key identity:** `Incurred = Paid + Change in IBNR`

---

## Input Table Schema

```sql
CREATE TABLE claims (
    cov_month  VARCHAR(7),   -- coverage month: 'yyyy-mm'
    paid_month VARCHAR(7),   -- payment month:  'yyyy-mm'
    paid_amt   MONEY
);
```

---

## The 10-Step Process

### Step 1: Build Raw Lag Triangle (pivot by coverage month)

```sql
SELECT
    paid_month,
    ROW_NUMBER() OVER (ORDER BY paid_month) - 1 AS r,
    SUM(CASE WHEN cov_month = @month01 THEN paid_amt ELSE 0 END) AS month01,
    SUM(CASE WHEN cov_month = @month02 THEN paid_amt ELSE 0 END) AS month02,
    -- ... through month12
    SUM(CASE WHEN cov_month = @month12 THEN paid_amt ELSE 0 END) AS month12
INTO #raw_triangle
FROM claims
WHERE paid_month BETWEEN @startDt AND @valDt
GROUP BY paid_month;
```

### Step 2: Lag Transform (align by development lag)

Self-join on row offset to shift each coverage month's payments into the correct lag column.

```sql
SELECT
    t01.paid_month,
    t01.r,
    t01.month01 AS c01,
    ISNULL(t02.month02, 0) AS c02,
    -- ... each column comes from a different lag offset
    ISNULL(t12.month12, 0) AS c12
INTO #lag_triangle
FROM #raw_triangle AS t01
LEFT JOIN #raw_triangle AS t02 ON t01.r = t02.r - 1
LEFT JOIN #raw_triangle AS t03 ON t01.r = t03.r - 2
-- ... through t12
```

### Step 3: Cumulative Paid Amounts

Self-join to accumulate: each row gets the sum of all prior lags.

```sql
SELECT
    s.r,
    SUM(t.c01) AS c01,
    SUM(t.c02) AS c02,
    -- ...
    SUM(t.c12) AS c12
INTO #cumulative
FROM #lag_triangle AS s
LEFT JOIN #lag_triangle AS t ON s.r >= t.r
GROUP BY s.r;
```

### Step 4: Loss Development Factors (age-to-age)

```sql
SELECT
    u.r,
    v.c01 / u.c01 AS c01,
    v.c02 / u.c02 AS c02,
    -- ...
    v.c12 / u.c12 AS c12
INTO #ldf_steps
FROM #cumulative AS u
INNER JOIN #cumulative AS v ON u.r = v.r - 1;
```

### Step 5: Truncated Average LDFs

Average of most recent 6 factors, excluding min and max.

```sql
CREATE FUNCTION dbo.trunc_avg (@v1 FLOAT, @v2 FLOAT, @v3 FLOAT, @v4 FLOAT, @v5 FLOAT, @v6 FLOAT)
RETURNS FLOAT AS
BEGIN
    DECLARE @min FLOAT = (SELECT MIN(x) FROM (VALUES (@v1),(@v2),(@v3),(@v4),(@v5),(@v6)) AS v(x));
    DECLARE @max FLOAT = (SELECT MAX(x) FROM (VALUES (@v1),(@v2),(@v3),(@v4),(@v5),(@v6)) AS v(x));
    RETURN (@v1 + @v2 + @v3 + @v4 + @v5 + @v6 - @min - @max) / 4;
END;
```

### Step 6: Compound Factors (tail to current)

Use a cursor to multiply LDFs backwards from tail to get cumulative development factor (CDF) for each coverage month.

### Step 7: Final Results

```sql
SELECT
    c.cov_month,
    SUM(paid_amt)                       AS paid_amt,
    SUM((1.0/l.cf - 1) * paid_amt)     AS ibnr,
    SUM(1.0/l.cf * paid_amt)           AS incurred_amt
FROM claims AS c
LEFT JOIN #ldf AS l ON c.cov_month = l.cov_month
GROUP BY c.cov_month
ORDER BY c.cov_month;
```

---

## Advantages of SQL over Spreadsheet

| Advantage | Detail |
|-----------|--------|
| Automation | Attach to a trigger; updates when claims data loads |
| Auditability | Code is fixed; no manual cell manipulation |
| Integration | Results pipe directly into R (Bornhuetter-Ferguson) |
| Separation | Logic lives in procedure; data lives in tables |

## Limitations

- Hard to incorporate professional judgment / manual overrides
- Less suitable for ad hoc sensitivity analysis
- Audit trail harder to show than spreadsheet trail

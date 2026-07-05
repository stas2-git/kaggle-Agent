# P&C Insurance Database Schema Guide

Use this file when: the user provides unfamiliar table names, asks about schema design, or you need to understand how an insurance database is typically structured before writing a join.

---

## The Standard Hierarchy

P&C insurance data almost always flows in this direction:

```
Party / Policyholder
    └── Policy (exposure universe — the table that must keep all rows)
            ├── Claim (loss events — subset of policies)
            │       └── Payment / Reserve (money events on a claim)
            └── Exposure (earned premium, units)
```

**Rule:** Always drive joins FROM the Policy table outward. LEFT JOIN to claims so zero-claim policies survive.

---

## Industry Standard: Property Casualty Data Model (PCDM)

The Object Management Group's PCDM organizes a P&C insurer's data into 13 Subject Area Models (SAMs). Knowing these helps you recognize what a table is doing even when column names are unfamiliar.

| SAM | What It Covers | Typical Table Names |
|-----|---------------|-------------------|
| **Party** | Policyholders, firms, staff | `parties`, `policyholders`, `customers` |
| **Account & Agreement** | Legal agreements, contracts | `accounts`, `agreements` |
| **Policy** | Policy details, limits, deductibles, dates | `policies`, `policy_terms`, `coverages` |
| **Claim** | Claim events, dates, adjusters, damages | `claims`, `claim_events`, `incidents` |
| **Assessment** | Credit scores, appraisals | `assessments`, `appraisals` |
| **Insurable Object** | Cars, buildings — what is insured | `vehicles`, `properties`, `insured_objects` |
| **Money** | Premiums, loss payments, reserves | `payments`, `reserves`, `transactions`, `premiums` |
| **Event** | Policy inception, cancellation, claim occurrence | `policy_events`, `claim_events` |
| **Product Coverage** | Coverage types and product definitions | `coverages`, `products`, `coverage_types` |

---

## Canonical Actuarial Schema (Minimal Working Set)

```sql
-- Exposure universe
CREATE TABLE policies (
    policy_id       INT PRIMARY KEY,
    policyholder_id INT,
    policy_type     VARCHAR(50),    -- 'auto', 'property', 'liability', 'life'
    effective_date  DATE,
    expiry_date     DATE,
    earned_premium  DECIMAL(12, 2),
    exposure_units  DECIMAL(10, 4)  -- car-years, house-years, etc.
);

-- Loss events
CREATE TABLE claims (
    claim_id         INT PRIMARY KEY,
    policy_id        INT,           -- FK to policies
    accident_date    DATE,
    report_date      DATE,
    accident_year    INT,           -- EXTRACT(YEAR FROM accident_date) — store as INT
    development_year INT,           -- year the payment was recorded
    paid_amount      DECIMAL(12, 2),
    case_reserve     DECIMAL(12, 2),
    incurred_amount  DECIMAL(12, 2) GENERATED ALWAYS AS (paid_amount + case_reserve),
    claim_status     VARCHAR(20)    -- 'open', 'closed', 'reopened', 'denied'
);

-- Name/demographic lookup
CREATE TABLE policyholders (
    policyholder_id INT PRIMARY KEY,
    name            VARCHAR(255),
    date_of_birth   DATE,
    gender          CHAR(1)
);
```

---

## Reading Unfamiliar Tables

When you receive table names you don't recognize, map them to this hierarchy before writing any SQL:

1. **Which table is the exposure universe?** Look for: `policies`, `policy_terms`, `contracts`, `accounts`. This is your LEFT table.
2. **Which table contains losses?** Look for: `claims`, `losses`, `incidents`, `loss_events`. LEFT JOIN from exposure to here.
3. **Which table is a lookup/dimension?** Look for: `policyholders`, `parties`, `coverages`, `claim_types`. Join with INNER or LEFT depending on whether missing lookups are acceptable.
4. **Which table contains money?** Look for: `payments`, `reserves`, `transactions`. May need to aggregate before joining to policy level.

---

## Common Schema Patterns to Watch For

### Separate paid and reserve tables
Some systems store paid losses and case reserves in separate tables. You need both for incurred:
```sql
-- Incurred = paid + reserve
SELECT
    p.policy_id,
    COALESCE(SUM(pay.paid_amount), 0)    AS total_paid,
    COALESCE(SUM(res.reserve_amount), 0) AS total_reserve,
    COALESCE(SUM(pay.paid_amount), 0)
        + COALESCE(SUM(res.reserve_amount), 0) AS total_incurred
FROM policies AS p
LEFT JOIN payments AS pay ON p.policy_id = pay.policy_id
LEFT JOIN reserves AS res ON p.policy_id = res.policy_id
GROUP BY p.policy_id;
```

### Claims with multiple payments (one-to-many)
A single claim may have many payment rows. Aggregate claims before joining to policies to avoid row multiplication:
```sql
WITH claim_totals AS (
    SELECT policy_id, SUM(paid_amount) AS total_paid
    FROM payments
    GROUP BY policy_id
)
SELECT p.policy_type, SUM(ct.total_paid) AS total_loss
FROM policies AS p
LEFT JOIN claim_totals AS ct ON p.policy_id = ct.policy_id
GROUP BY p.policy_type;
```

### Development year stored as a date, not an integer
If your data doesn't have a pre-computed `development_year` column:
```sql
EXTRACT(YEAR FROM payment_date) AS development_year,
EXTRACT(YEAR FROM accident_date) AS accident_year,
EXTRACT(YEAR FROM payment_date) - EXTRACT(YEAR FROM accident_date) AS dev_lag
```

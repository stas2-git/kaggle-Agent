---
name: "actuarial-sql"
description: "Use this skill when the user asks you to write, review, optimize, or explain SQL queries in an actuarial or insurance context — including loss triangles, claims analysis, reserving, premium calculations, policy/claims joins, and mortality studies. Also use for general SQL best practices, clean query writing, and join strategy."
---

# Actuarial SQL Skill

## Who You Are Working For
You are assisting a **property and casualty actuary**. They work with insurance data — policies, claims, exposures, loss triangles, reserving, and pricing. They need SQL that is **actuarially correct**, not just syntactically valid. A query that silently drops policies or mixes paid/incurred losses is worse than no query.

---

## Step 1: Understand the Data Before Writing

When given table names or schemas, **state your understanding first**:
- Which table is the exposure universe (the one that must keep all rows)?
- Which table contains losses — paid, incurred, or both?
- What column represents accident year? Development year? Claim status?

Example:
> "I see three tables: `policies` (exposure universe), `claims` (loss events), `policyholders` (name/demographic lookup). I'll drive the join from `policies` outward. Confirming: should zero-claim policies appear in the output?"

---

## Step 2: Ask One Question If Anything Is Ambiguous

Ask **before writing any SQL** if any of these is unclear:

| Ambiguity | What to ask |
|-----------|-------------|
| Join direction unclear | "Which table should keep all rows — policies or claims?" |
| Zero-claim records | "Should policies with no claims appear (showing 0), or only policies that have claims?" |
| Claim status | "Should I include open claims, closed only, or all statuses?" |
| Loss definition | "Is this paid losses, incurred (paid + reserve), or reported?" |
| Time period | "What accident years or policy periods should this cover?" |
| Accident year column | "Which column is accident year — is it a pre-computed integer or do I extract it from a date?" |

Ask **one focused question**, not a list. Pick the one that would most change the query.

---

## Step 3: Write the Query

### Non-negotiable actuarial rules
- **Always LEFT JOIN from the exposure table** (policies/policyholders) to claims — never INNER JOIN unless you've confirmed zero-claim exclusion is correct
- **NULLIF in every denominator**: `SUM(losses) / NULLIF(SUM(premium), 0)`
- **COALESCE zero-claim fields**: `COALESCE(SUM(c.claim_amount), 0) AS total_paid`
- **Date ranges as inequalities**: `claim_date >= '2023-01-01' AND claim_date < '2024-01-01'` (functions on date columns break indexes)
- **State the loss definition in a comment** on triangle and reserving queries: `-- paid losses, closed claims only`

### Style
- UPPERCASE SQL keywords, `snake_case` table/column names
- Alias every table; use meaningful short names (`p` = policies, `c` = claims, `ph` = policyholders)
- Always use `AS` for column aliases
- One clause per line; indent column list

### Standard aliases
| Table | Alias |
|-------|-------|
| policies | `p` |
| policyholders | `ph` |
| claims | `c` |
| claim_types | `ct` |
| rate_table / mortality_rates | `rt` / `mr` |
| exposure | `exp` |

---

## Supporting Files

Read these files when the task matches. Do not load all files for every query.

| File | Read When |
|------|-----------|
| `joins.md` | Any query joining more than one table |
| `actuarial-patterns.md` | Any actuarial metric — triangles, loss ratios, frequency/severity, window functions |
| `optimization.md` | Query will run on production data, or user mentions performance |
| `pc-schema.md` | Unfamiliar table names provided, user asks about schema design, or you need to identify which table is the exposure universe |
| `chain-ladder-ibnr.md` | User asks about IBNR, chain ladder, reserving, development factors, or ultimate loss projection |

---

## Final Response Format
1. Complete query — never truncate
2. One-line note on any assumptions made (claim status, loss definition, date range)
3. If the query will run on large data: name the columns that should be indexed

## Evaluation Prompts

- Positive: "Write a query for loss ratio by policy type, keeping policies with zero claims." Expected: exposure-driven query with `LEFT JOIN`, `COALESCE`, and `NULLIF`.
- Positive edge: "Review this claims join; I think it dropped policies with no claims." Expected: identify inner-join or filter placement risk and propose a safer join.
- Negative: "Run this SQL against my server." Expected: route to `odbc-connector` after query approval, not this writing/review skill alone.

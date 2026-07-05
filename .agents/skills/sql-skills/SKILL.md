---
name: sql-router
description: Use when any SQL task is requested in an actuarial or insurance context — including writing queries, joining tables, building loss triangles, computing loss ratios, connecting to a database, exploring schema, or executing queries against a live server.
---

# SQL Skills Router

Use this router to select the right focused SQL skill. Route first, then load the selected skill's `SKILL.md` before acting.

## How To Route

1. Identify whether the task is about **writing SQL**, **executing SQL**, or **both**.
2. Pick the matching focused skill below.
3. Load that skill's `SKILL.md` before writing any query or running any command.

---

## Routing

### Write or Review SQL
Use `actuarial-sql` (`skills-library/sql-skills/actuarial-sql` in this repo) when:
- Writing a new query against policy, claims, exposure, or rate tables
- Joining multiple tables
- Building loss triangles or development factor queries
- Computing loss ratios, claim frequency, severity, or pure premiums
- Reviewing or optimizing an existing query
- Explaining what a query does or why a join is wrong

### Execute SQL Against a Live Database
Use `odbc-connector` (`skills-library/sql-skills/odbc-connector` in this repo) when:
- Connecting to a database server
- Exploring what tables and columns exist
- Running a query and returning results
- Verifying the connection or read-only status
- The user says "run it", "execute", "query the database", or "show me what's in the database"

---

## Combination Patterns

- **Write and run**: load `actuarial-sql` to write the query → show it to the user → get approval → load `odbc-connector` to execute via `connector.py`
- **New database, unknown schema**: load `odbc-connector` first (`--explore`) to discover tables and columns → then load `actuarial-sql` to write the query using what was found
- **Review only**: load `actuarial-sql` only — no execution needed
- **Debug a slow query**: load `actuarial-sql` — check joins, filters, and indexes

---

## Rules

- Always load the focused skill's `SKILL.md` before writing SQL or running commands.
- Never load both skills at once unless the task genuinely requires writing AND executing.
- If the schema is unknown, explore before writing — don't guess column names.

---

## Evaluation Prompts

- Positive: "Join these 3 tables and give me loss by policy type." Expected: `actuarial-sql`.
- Positive: "Connect to my SQL Server and show me what tables are available." Expected: `odbc-connector`.
- Positive: "Write a loss triangle query and run it against my database." Expected: `actuarial-sql` then `odbc-connector`.
- Positive: "Why did Copilot drop half my policies when joining?" Expected: `actuarial-sql`.
- Positive: "What claim statuses exist in my database?" Expected: `odbc-connector` (`--explore` or `--query`).
- Positive: "Optimize this query — it's running too slow." Expected: `actuarial-sql`.
- Positive: "Run the exploration queries on my server." Expected: `odbc-connector`.
- Negative: "Format this Excel file." Expected: no SQL skill — route to excel skills.
- Negative: "Explain what a CTE is." Expected: answer directly — no skill load needed for a simple explanation.

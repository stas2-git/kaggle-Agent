---
name: "odbc-connector"
description: "Use this skill when the user wants to connect to a database, explore its schema, or execute SQL queries against a live server. Pairs with the actuarial-sql skill: actuarial-sql writes the query, odbc-connector executes it via connector.py."
---

# ODBC Connector Skill

## Core Principle
The agent generates SQL. `connector.py` executes it. **Never rewrite or modify connector.py.** The safety guardrails live in that script — they are not suggestions for the agent to follow, they are enforced by the code.

---

## Setup (One Time)

1. Copy `config.template.json` → `config.json` and fill in credentials
2. Use a **read-only database account** (SELECT only — no INSERT/UPDATE/DELETE/DDL)
3. Install pyodbc: `pip install pyodbc`
4. Install ODBC Driver 18 for SQL Server (if using SQL Server)

---

## How to Call connector.py

### Test the connection
```bash
python connector.py --verify
```

### Explore the database schema (always run first on a new database)
```bash
python connector.py --explore
```

### Run a query
```bash
python connector.py --query "SELECT p.policy_type, COUNT(*) FROM policies AS p GROUP BY p.policy_type"
```

### Run a query with higher row cap
```bash
python connector.py --query "SELECT ..." --cap 5000
```

### Get results as JSON
```bash
python connector.py --query "SELECT ..." --json
```

---

## The Workflow Every Session

```
1. CONNECT   →  python connector.py --verify
2. EXPLORE   →  python connector.py --explore
3. UNDERSTAND   read the exploration output — identify tables, columns, date ranges, claim statuses
4. WRITE        use actuarial-sql skill to write the query
5. SHOW         display the full query to the user in a code block
6. APPROVE      wait for user to say yes before running
7. EXECUTE   →  python connector.py --query "..."
8. RETURN       show results and row count; note if capped
```

**Steps 5 and 6 are mandatory.** Always show the query and wait for approval before calling connector.py with --query.

---

## What connector.py Enforces (You Don't Need to Check These)

- Only SELECT and WITH (CTEs) are allowed — any other statement is blocked
- Row cap (default 1,000) — results are never larger unless --cap is passed
- Read-only account check on every connection
- Every query is logged to `query_log.jsonl` with timestamp and row count

---

## Supporting Files

| File | Read When |
|------|-----------|
| `exploration-queries.md` | Exploration output is confusing, or table/column names don't match expected actuarial schema |
| `execution-workflow.md` | Troubleshooting connection errors or unexpected output |
| `safety.md` | User asks what the safety rules are, or you need to explain why a query was blocked |

## Evaluation Prompts

- Positive: "Verify my database connection and show available tables." Expected: use `connector.py --verify`, then `--explore`.
- Positive edge: "Run this approved SELECT with a 5000 row cap and return JSON." Expected: execute with `--query`, `--cap 5000`, and `--json` after approval.
- Negative: "Write a chain-ladder query but don't run it." Expected: route to `actuarial-sql`, not live execution.

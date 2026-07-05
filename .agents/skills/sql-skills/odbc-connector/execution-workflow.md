# Execution Workflow — Troubleshooting Guide

connector.py handles execution. This file covers what to do when things go wrong.

---

## Common Errors

| Error Message | Likely Cause | Fix |
|---------------|-------------|-----|
| `Config file not found` | config.json doesn't exist | Copy config.template.json → config.json and fill in credentials |
| `Connection failed: Login failed` | Wrong username/password | Check config.json credentials |
| `Connection failed: Cannot open database` | Wrong database name or no access | Confirm database name; check account has access |
| `Blocked: query starts with 'DROP'` | Safety check triggered | Query contains a blocked keyword — rewrite as SELECT |
| `Query failed: Invalid column name` | Column doesn't exist in that table | Re-run `--explore` and check actual column names |
| `Query failed: Invalid object name` | Table doesn't exist | Re-run `--explore` to see available tables |
| `Query failed: timeout` | Query too slow | Add WHERE filters to reduce data; check indexes |
| `Driver not found` | ODBC driver not installed | Install "ODBC Driver 18 for SQL Server" from Microsoft |
| `pyodbc not installed` | Missing dependency | Run `pip install pyodbc` |

---

## Read-Only Check Failed

If `--verify` reports the account is not read-only:
1. Ask the user to create a separate read-only account with SELECT-only grants
2. Update config.json with the new credentials
3. Re-run `--verify`

Do not proceed with analysis on an account that has write access.

---

## Exploration Output Has Unexpected Table Names

If `--explore` runs but the table names don't match expected actuarial schema (`policies`, `claims`, etc.):
1. Read `exploration-queries.md` — it explains how to map unfamiliar names to the standard hierarchy
2. Identify which table is the exposure universe (largest table, or the one with policy/contract in the name)
3. Run column inspection manually:
```bash
python connector.py --query "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'your_table' ORDER BY ORDINAL_POSITION"
```

---

## Row Cap Hit

If results show `(capped at 1,000)`:
- Add a WHERE filter to the query to narrow the result set — preferred
- Or raise the cap if the full result set is genuinely needed:
```bash
python connector.py --query "..." --cap 10000
```
Always tell the user the results were capped and by how much.

---

## Viewing the Query Log

The log lives at `query_log.jsonl` in the same folder as connector.py. Each line is a JSON record:
```json
{"timestamp": "2025-06-24T09:15:32", "query": "SELECT ...", "rows_returned": 47, "capped": false, "error": ""}
```

To view recent queries:
```bash
python connector.py --query "SELECT 1"  # just to test
# then open query_log.jsonl
```

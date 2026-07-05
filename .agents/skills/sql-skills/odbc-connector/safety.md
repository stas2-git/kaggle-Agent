# Safety Rules — Reference

These rules are enforced by `connector.py`. This file documents what the script does — it is not a checklist for the agent to follow manually.

---

## What connector.py Blocks

**Only SELECT and WITH (CTEs) are allowed.** Any query not starting with these is rejected before execution.

**Blocked keywords — rejected anywhere in the query:**
`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `REPLACE`, `MERGE`, `EXEC`, `EXECUTE`, `GRANT`, `REVOKE`, `DENY`, `BACKUP`, `RESTORE`, `DBCC`

**Multi-statement injection** — blocked keywords after a semicolon are also caught.

---

## Row Cap

Default: **1,000 rows**. Raise with `--cap N` when the full result set is genuinely needed. The script fetches cap + 1 to detect overflow and warns the user if results were truncated.

---

## Read-Only Check

On every connection, connector.py probes whether the account can write by attempting an INSERT on a nonexistent table. A permission-denied error confirms the account is read-only. If the check fails, the user is warned.

---

## Audit Log

Every query is appended to `query_log.jsonl`:
- Timestamp
- Full query text
- Rows returned
- Whether results were capped
- Any error message

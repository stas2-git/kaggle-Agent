#!/usr/bin/env python3
"""
ODBC Connector — safe, read-only SQL execution for actuarial analysis.

Usage:
    python connector.py --query "SELECT ..."          # run a query
    python connector.py --explore                     # explore database schema
    python connector.py --schema TABLE_NAME           # inspect a table's columns
    python connector.py --verify                      # test connection + read-only check
    python connector.py --query "..." --cap 5000      # raise row cap for this run
    python connector.py --query "..." --json          # output as JSON
    python connector.py --query "..." --csv           # output as CSV
"""

from __future__ import annotations

import argparse
import csv as csv_module
import datetime
import hashlib
import io
import json
import re
import sys
from pathlib import Path

_pyodbc = None


def require_pyodbc():
    global _pyodbc
    if _pyodbc is None:
        try:
            import pyodbc as imported_pyodbc
        except ImportError:
            sys.exit("pyodbc not installed. Run: pip install pyodbc")
        imported_pyodbc.pooling = True
        _pyodbc = imported_pyodbc
    return _pyodbc

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CONFIG_PATH = Path(__file__).parent / "config.json"

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(
            f"Config file not found: {CONFIG_PATH}\n"
            "Copy config.template.json to config.json and fill in your credentials."
        )
    with open(CONFIG_PATH) as f:
        return json.load(f)

# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------

# Always blocked — regardless of any setting
ALWAYS_BLOCKED = [
    r"\bxp_\w+",       # extended stored procedures
    r"\bsp_\w+",       # system stored procedures
    r"\bKILL\b",
    r"\bSHUTDOWN\b",
]

# Blocked in read-only mode
READ_ONLY_BLOCKED = [
    r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b",
    r"\bDROP\b",   r"\bALTER\b",  r"\bTRUNCATE\b",
    r"\bCREATE\b", r"\bREPLACE\b",r"\bMERGE\b",
    r"\bEXEC\b",   r"\bEXECUTE\b",
    r"\bGRANT\b",  r"\bREVOKE\b", r"\bDENY\b",
    r"\bBACKUP\b", r"\bRESTORE\b",r"\bDBCC\b",
]

MAX_QUERY_LENGTH = 10_000

def _strip_comments(sql: str) -> str:
    """Remove -- line comments and /* block comments */ before analysis."""
    sql = re.sub(r"--[^\n]*", " ", sql)
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    return sql

def _normalize(sql: str) -> str:
    return " ".join(sql.split()).upper()

def _hash(sql: str) -> str:
    return hashlib.sha256(sql.encode()).hexdigest()[:12]

def safety_check(sql: str) -> tuple[bool, str]:
    """
    Returns (is_safe, reason).
    Strips comments before analysis so embedded keywords can't bypass the check.
    """
    if not sql.strip():
        return False, "Empty query."

    if len(sql) > MAX_QUERY_LENGTH:
        return False, f"Query exceeds {MAX_QUERY_LENGTH:,} character limit."

    # Multi-statement check
    if ";" in sql.strip().rstrip(";"):
        return False, "Multi-statement queries are not allowed."

    cleaned  = _strip_comments(sql)
    normalized = _normalize(cleaned)

    # Always-blocked patterns (regardless of mode)
    for pattern in ALWAYS_BLOCKED:
        if re.search(pattern, normalized):
            return False, f"Blocked: query contains always-banned pattern '{pattern}'."

    # Read-only: must start with SELECT or WITH
    if not re.match(r"^\s*(SELECT|WITH)\b", normalized):
        first_word = normalized.split()[0] if normalized.split() else "(empty)"
        return False, f"Blocked: only SELECT/WITH queries are allowed. Query starts with '{first_word}'."

    # Read-only blocked patterns
    for pattern in READ_ONLY_BLOCKED:
        if re.search(pattern, normalized):
            return False, f"Blocked: query contains write/DDL keyword matching '{pattern}'."

    return True, ""

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

_active_connection: object | None = None

def _ping(conn: object) -> bool:
    """Check if a connection is still alive."""
    try:
        conn.cursor().execute("SELECT 1")
        return True
    except Exception:
        return False

def get_connection(config: dict) -> object:
    """Return a live connection, reconnecting if stale."""
    global _active_connection
    if _active_connection is not None and _ping(_active_connection):
        return _active_connection
    pyodbc = require_pyodbc()

    driver  = config.get("driver", "ODBC Driver 18 for SQL Server")
    server  = config["server"]
    db      = config["database"]
    user    = config["username"]
    pwd     = config["password"]
    trust   = config.get("trust_server_certificate", "yes")
    timeout = config.get("timeout", 30)

    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={db};"
        f"UID={user};"
        f"PWD={pwd};"
        f"TrustServerCertificate={trust};"
    )
    conn = pyodbc.connect(conn_str, timeout=timeout, autocommit=True)
    conn.setdecoding(pyodbc.SQL_CHAR,  encoding="utf-8")
    conn.setdecoding(pyodbc.SQL_WCHAR, encoding="utf-8")
    conn.setencoding(encoding="utf-8")
    _active_connection = conn
    return conn

def verify_readonly(conn: object) -> bool:
    """Probe whether the account can write. Returns True if read-only."""
    pyodbc = require_pyodbc()
    try:
        conn.cursor().execute("INSERT INTO __safety_probe_xyz__ VALUES (1)")
        return False  # write succeeded
    except pyodbc.Error as e:
        msg = str(e).lower()
        return "permission" in msg or "denied" in msg

# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def _serialize(value) -> object:
    """Convert ODBC-specific types to JSON-safe values."""
    if value is None:
        return None
    if isinstance(value, (bytes, bytearray)):
        return "<binary>"
    if isinstance(value, bool):
        return value
    if hasattr(value, "isoformat"):   # date, datetime, time
        return value.isoformat()
    return value

def execute_query(conn: object, sql: str, cap: int) -> tuple:
    """Run query with safety check and row cap. Returns (columns, rows, overflow)."""
    safe, reason = safety_check(sql)
    if not safe:
        raise ValueError(reason)

    cursor = conn.cursor()
    cursor.execute(sql)
    columns = [desc[0] for desc in cursor.description] if cursor.description else []

    rows = []
    overflow = False
    batch_size = 500
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        for row in batch:
            if len(rows) >= cap:
                overflow = True
                break
            rows.append(tuple(_serialize(v) for v in row))
        if overflow:
            break

    return columns, rows, overflow

def get_table_list(conn: object) -> list:
    """List tables using ODBC metadata API, with SQL fallback."""
    cursor = conn.cursor()
    tables = []
    try:
        for t in cursor.tables():
            if t.table_type == "TABLE":
                tables.append({
                    "schema": t.table_schem or "",
                    "name":   t.table_name,
                })
        if tables:
            return tables
    except Exception:
        pass
    # SQL fallback
    cursor.execute(
        "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_SCHEMA, TABLE_NAME"
    )
    return [{"schema": r[0] or "", "name": r[1]} for r in cursor.fetchall()]

def get_table_schema(conn: object, table_name: str) -> list:
    """Return column info using ODBC metadata API, with SQL fallback."""
    cursor = conn.cursor()
    parts = table_name.split(".")
    schema = parts[0] if len(parts) > 1 else None
    tbl    = parts[-1]
    columns = []
    try:
        for col in cursor.columns(table=tbl, schema=schema):
            columns.append({
                "name":     col.column_name,
                "type":     col.type_name,
                "nullable": col.nullable == 1,
                "position": col.ordinal_position,
            })
        if columns:
            return columns
    except Exception:
        pass
    # SQL fallback
    cursor.execute(
        "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, ORDINAL_POSITION "
        "FROM INFORMATION_SCHEMA.COLUMNS "
        f"WHERE TABLE_NAME = ? ORDER BY ORDINAL_POSITION",
        (tbl,)
    )
    return [
        {"name": r[0], "type": r[1], "nullable": r[2] == "YES", "position": r[3]}
        for r in cursor.fetchall()
    ]

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _to_str(v) -> str:
    return "NULL" if v is None else ("true" if v is True else "false" if v is False else str(v))

def print_table(columns: list, rows: list):
    if not rows:
        print("(no rows returned)")
        return
    widths = [len(c) for c in columns]
    str_rows = [[_to_str(v) for v in row] for row in rows]
    for sr in str_rows:
        for i, v in enumerate(sr):
            widths[i] = max(widths[i], len(v))
    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    hdr = "| " + " | ".join(c.ljust(widths[i]) for i, c in enumerate(columns)) + " |"
    print(sep); print(hdr); print(sep)
    for sr in str_rows:
        print("| " + " | ".join(v.ljust(widths[i]) for i, v in enumerate(sr)) + " |")
    print(sep)

def print_json(columns: list, rows: list):
    print(json.dumps(
        [dict(zip(columns, row)) for row in rows],
        indent=2, default=str
    ))

def print_csv(columns: list, rows: list):
    out = io.StringIO()
    w = csv_module.writer(out)
    w.writerow(columns)
    for row in rows:
        w.writerow([_to_str(v) for v in row])
    print(out.getvalue(), end="")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_PATH = Path(__file__).parent / "query_log.jsonl"

def log_query(sql: str, rows_returned: int, capped: bool, error: str = ""):
    entry = {
        "timestamp":     datetime.datetime.now().isoformat(),
        "sql_hash":      _hash(sql),         # hash only — no raw SQL in log
        "rows_returned": rows_returned,
        "capped":        capped,
        "error":         error,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

# ---------------------------------------------------------------------------
# Exploration
# ---------------------------------------------------------------------------

EXPLORE_QUERIES = {
    "date_range": "SELECT MIN(claim_date) AS earliest, MAX(claim_date) AS latest, COUNT(*) AS total FROM claims",
    "claim_status_breakdown": "SELECT claim_status, COUNT(*) AS cnt FROM claims GROUP BY claim_status ORDER BY cnt DESC",
    "policy_type_breakdown":  "SELECT policy_type, COUNT(*) AS cnt FROM policies GROUP BY policy_type ORDER BY cnt DESC",
    "claim_amount_stats": (
        "SELECT COUNT(*) AS total_rows, COUNT(claim_amount) AS non_null, "
        "MIN(claim_amount) AS min_amt, MAX(claim_amount) AS max_amt, "
        "AVG(claim_amount) AS avg_amt, SUM(claim_amount) AS total_paid FROM claims"
    ),
    "accident_years": (
        "SELECT accident_year, COUNT(*) AS claims, SUM(claim_amount) AS total_paid "
        "FROM claims GROUP BY accident_year ORDER BY accident_year"
    ),
}

def run_exploration(conn: object, config: dict):
    print("\n=== DATABASE EXPLORATION ===\n")

    # Tables overview (uses metadata API)
    print("--- Tables ---")
    try:
        tables = get_table_list(conn)
        for t in tables:
            schema = f"{t['schema']}." if t['schema'] else ""
            print(f"  {schema}{t['name']}")
    except Exception as e:
        print(f"  Could not list tables: {e}")
    print()

    # Schema query cap is relaxed — metadata only
    schema_cap = 200

    for name, sql in EXPLORE_QUERIES.items():
        print(f"--- {name.replace('_', ' ').title()} ---")
        try:
            cols, rows, overflow = execute_query(conn, sql, cap=schema_cap)
            print_table(cols, rows)
            if overflow:
                print(f"  (capped at {schema_cap} rows)")
            log_query(sql, len(rows), overflow)
        except Exception as e:
            print(f"  Skipped ({e})")
        print()

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Safe ODBC connector for actuarial SQL.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query",   type=str,          help="SQL SELECT query to execute")
    group.add_argument("--explore", action="store_true",help="Run exploration queries")
    group.add_argument("--schema",  type=str,          help="Show columns for TABLE_NAME")
    group.add_argument("--verify",  action="store_true",help="Test connection and read-only status")
    parser.add_argument("--cap",    type=int, default=None, help="Row cap override")
    parser.add_argument("--json",   action="store_true", help="Output as JSON")
    parser.add_argument("--csv",    action="store_true", help="Output as CSV")
    args = parser.parse_args()

    config  = load_config()
    row_cap = args.cap or config.get("row_cap", 1000)

    try:
        conn = get_connection(config)
    except Exception as e:
        sys.exit(f"Connection failed: {e}")

    print(f"Connected: {config['server']} / {config['database']}")

    readonly_ok = verify_readonly(conn)
    if not readonly_ok:
        print("WARNING: Account may not be read-only. Use a SELECT-only database account.")

    if args.verify:
        print(f"Read-only check: {'PASS' if readonly_ok else 'FAIL'}")
        return

    if args.explore:
        run_exploration(conn, config)
        return

    if args.schema:
        try:
            cols = get_table_schema(conn, args.schema)
            if not cols:
                print(f"No columns found for '{args.schema}'.")
            else:
                print(f"\nSchema: {args.schema}\n")
                for c in cols:
                    null = "NULL" if c["nullable"] else "NOT NULL"
                    print(f"  {c['position']:>3}.  {c['name']:<30}  {c['type']:<20}  {null}")
        except Exception as e:
            sys.exit(f"Schema lookup failed: {e}")
        return

    if args.query:
        safe, reason = safety_check(args.query)
        if not safe:
            log_query(args.query, 0, False, error=reason)
            sys.exit(f"\n{reason}\n")

        try:
            cols, rows, overflow = execute_query(conn, args.query, cap=row_cap)
        except Exception as e:
            log_query(args.query, 0, False, error=str(e))
            sys.exit(f"Query failed: {e}")

        if args.json:
            print_json(cols, rows)
        elif args.csv:
            print_csv(cols, rows)
        else:
            print_table(cols, rows)

        print(f"\n{len(rows)} row(s) returned", end="")
        if overflow:
            print(f" (capped at {row_cap} — use --cap N to raise)", end="")
        print()

        log_query(args.query, len(rows), overflow)


if __name__ == "__main__":
    main()

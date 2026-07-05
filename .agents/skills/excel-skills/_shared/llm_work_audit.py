from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha1
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


NY_TZ = ZoneInfo("America/New_York")
SCHEMA_VERSION = "2.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def timestamp_run_id() -> str:
    return datetime.now(NY_TZ).strftime("%Y-%m-%dT%H-%M-%S")


def resolve_path(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return dict(default)


def file_metadata(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    resolved = resolve_path(path)
    exists = resolved.exists()
    return {
        "path": str(resolved),
        "exists": exists,
        "bytes": resolved.stat().st_size if exists else None,
        "modified_at_utc": datetime.fromtimestamp(resolved.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat()
        if exists
        else None,
    }


def workbook_metadata(path: str | Path) -> dict[str, Any]:
    resolved = resolve_path(path)
    stat = resolved.stat()
    return {
        "path": str(resolved),
        "name": resolved.name,
        "bytes": stat.st_size,
        "modified_at_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat(),
        "fingerprint": f"{stat.st_size}:{stat.st_mtime_ns}",
    }


def task_fingerprint(task: str | None) -> str | None:
    if not task:
        return None
    normalized = " ".join(task.split()).strip().lower()
    if not normalized:
        return None
    return sha1(normalized.encode("utf-8")).hexdigest()[:12]


def infer_llm_work_root(workbook_path: Path, llm_work_root_value: str | None) -> Path:
    return resolve_path(llm_work_root_value) if llm_work_root_value else (workbook_path.parent / "llm_work").resolve()


def infer_run_context(path: Path) -> tuple[Path | None, str | None]:
    parts = path.parts
    if "llm_work" not in parts or "runs" not in parts:
        return None, None
    runs_index = parts.index("runs")
    if runs_index + 1 >= len(parts):
        return None, None
    llm_work_index = parts.index("llm_work")
    llm_root = Path(parts[0])
    for part in parts[1 : llm_work_index + 1]:
        llm_root /= part
    return llm_root, parts[runs_index + 1]


def run_root(llm_work_root: Path, run_id: str) -> Path:
    return llm_work_root / "runs" / run_id


def artifacts_dir(llm_work_root: Path, run_id: str) -> Path:
    return run_root(llm_work_root, run_id) / "artifacts"


def artifact_path(llm_work_root: Path, run_id: str, filename: str) -> Path:
    return artifacts_dir(llm_work_root, run_id) / filename


def current_dir(llm_work_root: Path) -> Path:
    return llm_work_root / "current"


def current_state_path(llm_work_root: Path) -> Path:
    return current_dir(llm_work_root) / "state.json"


def latest_run_path(llm_work_root: Path) -> Path:
    return current_dir(llm_work_root) / "latest_run.json"


def current_context_path(llm_work_root: Path) -> Path:
    return current_dir(llm_work_root) / "context.md"


def normalize_artifacts(artifacts: dict[str, Any] | None) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    if not artifacts:
        return normalized
    for key, value in artifacts.items():
        if value is None:
            normalized[key] = None
        elif isinstance(value, dict) and "path" in value:
            normalized[key] = value
        elif isinstance(value, (str, Path)):
            normalized[key] = file_metadata(value)
        else:
            normalized[key] = value
    return normalized


def load_current_state(llm_work_root: Path) -> dict[str, Any]:
    return load_json(
        current_state_path(llm_work_root),
        {"schema_version": SCHEMA_VERSION, "artifacts": {}, "warnings": []},
    )


def artifacts_exist(state: dict[str, Any], keys: list[str]) -> bool:
    artifacts = state.get("artifacts") or {}
    for key in keys:
        meta = artifacts.get(key)
        if not isinstance(meta, dict) or not meta.get("exists") or not meta.get("path"):
            return False
        if not Path(meta["path"]).exists():
            return False
    return True


def can_reuse_for_workbook(
    llm_work_root: Path,
    workbook: dict[str, Any],
    artifact_keys: list[str],
    *,
    task_hash: str | None = None,
) -> tuple[bool, dict[str, Any]]:
    state = load_current_state(llm_work_root)
    current_workbook = state.get("workbook") or {}
    same_workbook = (
        current_workbook.get("path") == workbook.get("path")
        and current_workbook.get("fingerprint") == workbook.get("fingerprint")
    )
    same_task = task_hash is None or state.get("task_fingerprint") == task_hash
    reusable = same_workbook and same_task and artifacts_exist(state, artifact_keys)
    return reusable, state


def render_context(state: dict[str, Any]) -> str:
    workbook = state.get("workbook") or {}
    artifacts = state.get("artifacts") or {}
    lines = [
        "# Current Workbook State",
        "",
        f"- Workbook: `{workbook.get('path', 'unknown')}`",
        f"- Latest run: `{state.get('latest_run_id', 'unknown')}`",
        f"- Latest successful run: `{state.get('latest_successful_run_id', 'unknown')}`",
        f"- Last event: `{state.get('latest_event_type', 'unknown')}`",
        f"- Last status: `{state.get('latest_status', 'unknown')}`",
    ]
    if workbook.get("modified_at_utc"):
        lines.append(f"- Workbook modified: `{workbook['modified_at_utc']}`")
    if state.get("task"):
        lines.append(f"- Last task: {state['task']}")
    if state.get("backup_policy"):
        lines.append(f"- Backup policy: `{state['backup_policy']}`")
    if state.get("backup_outcome"):
        lines.append(f"- Backup outcome: `{state['backup_outcome']}`")
    lines.append("")
    lines.append("## Artifacts")
    for key, meta in artifacts.items():
        if not meta or not isinstance(meta, dict):
            continue
        lines.append(f"- {key}: `{meta.get('path')}`")
    warnings = state.get("warnings") or []
    if warnings:
        lines.append("")
        lines.append("## Warnings")
        for item in warnings:
            lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def update_current_files(llm_work_root: Path, event: dict[str, Any]) -> None:
    current = current_dir(llm_work_root)
    current.mkdir(parents=True, exist_ok=True)

    state = load_json(
        current_state_path(llm_work_root),
        {
            "schema_version": SCHEMA_VERSION,
            "artifacts": {},
            "warnings": [],
        },
    )
    state["schema_version"] = SCHEMA_VERSION
    state["latest_run_id"] = event.get("run_id")
    state["latest_event_id"] = event.get("event_id")
    state["latest_event_type"] = event.get("event_type")
    state["latest_event_at_utc"] = event.get("timestamp_utc")
    state["latest_status"] = event.get("status")
    if event.get("status") == "completed":
        state["latest_successful_run_id"] = event.get("run_id")

    workbook = event.get("workbook")
    if workbook:
        state["workbook"] = workbook

    if event.get("task") is not None:
        state["task"] = event.get("task")
        state["task_fingerprint"] = event.get("task_fingerprint")

    if event.get("backup_policy"):
        state["backup_policy"] = event.get("backup_policy")
    if event.get("backup_outcome"):
        state["backup_outcome"] = event.get("backup_outcome")

    artifacts = normalize_artifacts(event.get("artifacts"))
    if artifacts:
        state.setdefault("artifacts", {}).update(artifacts)

    summary = event.get("summary") or {}
    warnings = []
    if isinstance(summary, dict):
        for key in ("warning", "warnings"):
            value = summary.get(key)
            if isinstance(value, str):
                warnings.append(value)
            elif isinstance(value, list):
                warnings.extend(str(item) for item in value)
    state["warnings"] = warnings

    state_path = current_state_path(llm_work_root)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    latest_run_path(llm_work_root).write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "run_id": event.get("run_id"),
                "event_id": event.get("event_id"),
                "event_type": event.get("event_type"),
                "timestamp_utc": event.get("timestamp_utc"),
                "status": event.get("status"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    current_context_path(llm_work_root).write_text(render_context(state), encoding="utf-8")


def append_run_event(
    llm_work_root: Path,
    run_id: str,
    event: dict[str, Any],
    *,
    update_current: bool = True,
) -> Path:
    log_path = run_root(llm_work_root, run_id) / "run_log.json"
    payload = load_json(
        log_path,
        {"schema_version": SCHEMA_VERSION, "run_id": run_id, "events": []},
    )
    events = payload.setdefault("events", [])
    event = dict(event)
    event["run_id"] = run_id
    event.setdefault("event_id", f"{run_id}:{len(events) + 1:04d}")
    if "artifacts" in event:
        event["artifacts"] = normalize_artifacts(event["artifacts"])
    events.append(event)
    payload["schema_version"] = SCHEMA_VERSION
    payload["updated_at_utc"] = utc_now()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if update_current:
        update_current_files(llm_work_root, event)
    return log_path

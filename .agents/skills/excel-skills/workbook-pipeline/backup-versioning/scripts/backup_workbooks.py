#!/usr/bin/env python3
"""Create timestamped workbook backups and optional working copies."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from _shared.llm_work_audit import (  # type: ignore  # noqa: E402
    append_run_event,
    artifact_path,
    file_metadata,
    infer_llm_work_root,
    infer_run_context,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create timestamped backups and optional working copies for workbook jobs."
    )
    parser.add_argument("--manifest", help="Path to a manifest JSON file from batch-intake.")
    parser.add_argument(
        "--file",
        action="append",
        default=[],
        help="Explicit workbook file to back up. Can be passed multiple times.",
    )
    parser.add_argument(
        "--backup-root",
        help="Directory under which a timestamped backup run folder will be created.",
    )
    parser.add_argument(
        "--create-working-copies",
        action="store_true",
        help="Also create editable working copies in a sibling working tree.",
    )
    parser.add_argument(
        "--edit-target",
        choices=("original", "working_copy"),
        default="original",
        help="Where downstream edits should normally land. Defaults to editing the original workbook after backup.",
    )
    parser.add_argument(
        "--output",
        help="Optional path for the mapping JSON. Defaults to <run_dir>/backup-map.json",
    )
    parser.add_argument(
        "--llm-work-root",
        help="Optional llm_work directory. Used to infer backup paths when --backup-root is omitted.",
    )
    parser.add_argument(
        "--run-id",
        help="Optional llm_work run id. Used with --llm-work-root when no manifest path is available.",
    )
    parser.add_argument(
        "--no-mirror-current",
        action="store_true",
        help="Do not update llm_work/current state files for this run.",
    )
    args = parser.parse_args()
    if not args.manifest and not args.file:
        parser.error("At least one of --manifest or --file is required.")
    if args.edit_target == "working_copy":
        args.create_working_copies = True
    return args


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")


def resolve_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_relative_path(record: dict, used_relatives: set[str]) -> Path:
    relative = record.get("relative_to_root") or record.get("name") or Path(record["path"]).name
    relative_path = Path(str(relative))
    candidate = relative_path
    counter = 2
    while candidate.as_posix() in used_relatives:
        candidate = candidate.with_name(f"{candidate.stem}-{counter}{candidate.suffix}")
        counter += 1
    used_relatives.add(candidate.as_posix())
    return candidate


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def build_records_from_manifest(manifest: dict) -> list[dict]:
    workbooks = manifest.get("workbooks", [])
    if not isinstance(workbooks, list):
        raise ValueError("Manifest is missing a valid 'workbooks' list.")
    return workbooks


def build_records_from_files(files: list[str]) -> list[dict]:
    records = []
    for file_value in files:
        path = resolve_path(file_value)
        records.append(
            {
                "name": path.name,
                "path": str(path),
                "relative_to_root": path.name,
                "source": "explicit_file",
            }
        )
    return records


def infer_llm_work_root(args: argparse.Namespace, manifest_path: Path | None) -> Path | None:
    if args.llm_work_root:
        return resolve_path(args.llm_work_root)

    if manifest_path:
        for parent in manifest_path.parents:
            if parent.name == "llm_work":
                return parent

    if args.file:
        parents = {resolve_path(value).parent for value in args.file}
        if len(parents) == 1:
            return next(iter(parents)) / "llm_work"

    return None


def infer_backup_root(args: argparse.Namespace, manifest_path: Path | None) -> tuple[Path, Path | None]:
    if args.backup_root:
        return resolve_path(args.backup_root), None

    llm_work_root = infer_llm_work_root(args, manifest_path)
    if llm_work_root is None:
        raise ValueError("Could not infer backup root. Pass --backup-root, or use a manifest/file path tied to a workbook folder.")

    if manifest_path and "runs" in manifest_path.parts:
        run_index = manifest_path.parts.index("runs")
        if run_index + 1 < len(manifest_path.parts):
            run_id = manifest_path.parts[run_index + 1]
            run_root = llm_work_root / "runs" / run_id
            return run_root / "backups", None

    run_id = args.run_id or now_stamp()
    run_root = llm_work_root / "runs" / run_id
    return run_root / "backups", None


def main() -> int:
    args = parse_args()
    started_at = datetime.now(timezone.utc)
    manifest_path = resolve_path(args.manifest) if args.manifest else None
    manifest = load_manifest(manifest_path) if manifest_path else None
    try:
        backup_root, _current_output_path = infer_backup_root(args, manifest_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    backup_root.mkdir(parents=True, exist_ok=True)

    records = []
    if manifest is not None:
        records.extend(build_records_from_manifest(manifest))
    if args.file:
        records.extend(build_records_from_files(args.file))

    if backup_root.name == "backups":
        run_dir = backup_root.parent
        backups_dir = backup_root
        working_dir = run_dir / "working"
        backups_dir.mkdir(parents=True, exist_ok=True)
        if args.create_working_copies:
            working_dir.mkdir(parents=True, exist_ok=True)
    else:
        run_dir = backup_root / f"run-{now_stamp()}"
        if run_dir.exists():
            raise FileExistsError(f"Backup run directory already exists: {run_dir}")
        backups_dir = run_dir / "backups"
        working_dir = run_dir / "working"
        backups_dir.mkdir(parents=True, exist_ok=False)
        if args.create_working_copies:
            working_dir.mkdir(parents=True, exist_ok=False)

    used_relatives: set[str] = set()
    copied: list[dict[str, object]] = []
    missing: list[dict[str, str]] = []

    for record in records:
        source = resolve_path(record["path"])
        if not source.exists():
            missing.append({"path": str(source), "reason": "file_not_found"})
            continue
        if not source.is_file():
            missing.append({"path": str(source), "reason": "path_is_not_file"})
            continue

        relative_path = safe_relative_path(record, used_relatives)
        backup_path = backups_dir / relative_path
        if backup_path.exists():
            raise FileExistsError(f"Backup target already exists: {backup_path}")
        copy_file(source, backup_path)

        working_path = None
        if args.create_working_copies:
            working_path = working_dir / relative_path
            if working_path.exists():
                raise FileExistsError(f"Working-copy target already exists: {working_path}")
            copy_file(source, working_path)

        copied.append(
            {
                "name": record.get("name", source.name),
                "source_path": str(source),
                "relative_path": relative_path.as_posix(),
                "backup_path": str(backup_path),
                "working_path": str(working_path) if working_path else None,
                "source": record.get("source", "unknown"),
            }
        )

    llm_work_root, run_id = infer_run_context(backups_dir)
    output_path = resolve_path(args.output) if args.output else (artifact_path(llm_work_root, run_id, "backup-map.json") if llm_work_root and run_id else (backups_dir / "backup-map.json"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "run_dir": str(run_dir),
        "backup_dir": str(backups_dir),
        "manifest_path": str(manifest_path) if manifest_path else None,
        "create_working_copies": args.create_working_copies,
        "edit_target": args.edit_target,
        "summary": {
            "copied_count": len(copied),
            "missing_count": len(missing),
        },
        "copied": copied,
        "missing": missing,
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    run_log_path = None
    if llm_work_root and run_id:
        completed_at = datetime.now(timezone.utc)
        run_log_path = append_run_event(
            llm_work_root,
            run_id,
            {
                "event_type": "workbook-backup.completed",
                "timestamp_utc": completed_at.replace(microsecond=0).isoformat(),
                "started_at_utc": started_at.replace(microsecond=0).isoformat(),
                "duration_ms": int((completed_at - started_at).total_seconds() * 1000),
                "skill": "workbook-backup-versioning",
                "status": "completed",
                "source_file": copied[0]["source_path"] if len(copied) == 1 else (str(manifest_path) if manifest_path else str(output_path)),
                "artifacts": {
                    "backup_map": file_metadata(output_path),
                    "backup_dir": file_metadata(backups_dir),
                    "working_dir": file_metadata(working_dir) if args.create_working_copies else None,
                },
                "summary": {
                    "copied_count": len(copied),
                    "missing_count": len(missing),
                    "create_working_copies": args.create_working_copies,
                    "edit_target": args.edit_target,
                },
            },
            update_current=not args.no_mirror_current,
        )

    print(f"Backup run directory: {run_dir}")
    print(f"Mapping file: {output_path}")
    if run_log_path:
        print(f"Wrote run log: {run_log_path}")
    print(f"Copied workbooks: {len(copied)}")
    print(f"Edit target: {args.edit_target}")
    if args.create_working_copies:
        print("Working copies: enabled")
    if missing:
        print(f"Missing entries: {len(missing)}")
    return 0 if copied else 1


if __name__ == "__main__":
    sys.exit(main())

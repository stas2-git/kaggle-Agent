---
name: workbook-backup-versioning
description: Use when a workflow is about to change one or more Excel workbooks and needs timestamped backups, working copies, or other reversible safety rails before VBA injection or rebuild steps.
---

# Workbook Backup Versioning

Use this skill before any autonomous workbook modification.

## What this skill is for

- Create timestamped backups of target workbooks
- Optionally create separate working copies for cautious or high-risk edits
- Preserve original paths alongside editable copies
- Record backup metadata for rollback and reporting

## Core workflow

1. Read the job manifest or explicit workbook list.
2. Create a backup root inside the current run folder with a run timestamp.
3. Copy each workbook to a safe backup location.
4. Default downstream edits to the original workbook unless the run explicitly chooses `working_copy`.
5. Optionally create a second working copy for cautious edits.
6. Emit a mapping from original path to backup path, working path, and intended edit target.
7. Append a backup event to the run log.

## Expected output

- A backup folder containing untouched workbook copies
- A mapping file that downstream automation can read

## Command pattern

```bash
python3 skills/workbook-pipeline/backup-versioning/scripts/backup_workbooks.py \
  --manifest "/path/to/workbook-folder/llm_work/manifests/workbook-job.json"
```

For a cautious run that should edit a copy instead:

```bash
python3 skills/workbook-pipeline/backup-versioning/scripts/backup_workbooks.py \
  --manifest "/path/to/workbook-folder/llm_work/manifests/workbook-job.json" \
  --edit-target working_copy
```

## Notes

- Preserve file extensions exactly.
- Never overwrite an existing backup folder silently.
- Default to copy, not move.
- Default edit mode should be `original`, so the user can keep working in the same workbook they already have open.
- Use `working_copy` only for explicitly cautious runs, high-risk formula work, or batch scenarios where touching the original immediately would be risky.
- If `--backup-root` is omitted and the manifest or workbook is already tied to `llm_work/`, default to the active run folder and mirror the latest backup map into `llm_work/current/backups/`.
- In the active run layout, workbook copies now live directly in `llm_work/runs/<timestamp>/backups/` instead of another nested timestamp folder.
- Run folder timestamps use New York local time so they match the user’s day-to-day workflow more naturally.
- Prefer a workbook-local artifact root such as `llm_work/runs/<timestamp>/backups/` so original, backup, and working-copy paths stay easy to inspect together.
- Also write the step outcome into `llm_work/runs/<timestamp>/run_log.json`.
- Always create a fresh backup for each new improvement run, even if earlier backups already exist.
- Preserve prior runs under `llm_work/runs/<timestamp>/`; do not reuse old working copies as the new default.

## Evaluation Prompts

- Positive: "Before editing these two workbooks, create timestamped backups." Expected: backup map and untouched copies.
- Positive edge: "This formula change is risky; make a working copy instead of editing original." Expected: backup plus `working_copy` edit target.
- Negative: "Tell me what sheets are in the workbook." Expected: use decomposition or inspection, not backup.

# Artifacts

This folder is the evidence trail for the build-gate process defined in
[`../../spec_files/50_implementation/02_spec_adequacy_and_build_gates.md`](../../spec_files/50_implementation/02_spec_adequacy_and_build_gates.md).
That spec defines 8 gates (0-7) a capstone build is supposed to pass through; each
subfolder here is where one or more of those gates writes its proof. This is not a "build
once, evidence sits forever unread" folder — some of these are one-time snapshots, others
are meant to be re-run and appended to as the project changes. See the table below.

## What's here and whether it's one-time or ongoing

| Folder / file | Gate | One-time or ongoing? | What it proves |
|---|---|---|---|
| `spec_reviews/` | Gate 0 — Spec Completeness Review | One-time per major spec version | A fresh read of the spec package, before writing code, confirming the MVP/tools/tests are unambiguous enough to start. Re-run only after a major spec rewrite (hence `spec_review_v1.md`, `spec_review_v2_adk_upgrade.md`). |
| `build_plans/` | Gate 1 — Plan-Only Build Review | One-time per major build phase | The implementation plan (file tree, tool contracts, test list) written *before* touching code. A historical record of what was planned, not something you update after the fact. |
| `gate_results/` | Gates 2, 3, 4, 6, 7 | **Mixed** — see below | Proof that a specific gate passed, with real command output. |
| `rebuilds/` | Gate 5 — Fresh-Context Rebuild Test | Ongoing — re-run whenever the spec package changes materially | Whether a builder with *no access to the real implementation* can rebuild a working vertical slice from `spec_files/` alone. Each attempt gets its own `vX/` subfolder (see below). |
| `spec_change_log.md` | Section 10 — Spec Update Rules | **Ongoing, never "done"** | A running ledger: every time implementation reveals a spec gap, this records what changed, why, and what classification it was (code defect / spec gap / missing requirement / etc.). Grows for the life of the project. |
| `traces/` | Supports Gate 7F (Agents CLI eval) | Ongoing, currently empty | Reserved for `agents-cli eval generate`/`grade` trace output. Empty because Gate 7 Phase 10 (see `gate_results/gate_7_adk_upgrade.md`) is blocked on Google Cloud Application Default Credentials not being configured in this environment — not a bug, just unrun. |

### `gate_results/` in detail — why it's not all "one-time"

- `gate_2_vertical_slice.md`, `gate_3_golden_tests.md`, `gate_4_agent_evals.md` — **one-time
  checkpoints.** Each proves a specific build milestone was reached once. They don't need
  re-running unless that milestone's behavior materially regresses.
- `gate_6_submission_readiness.md` — **meant to be re-run before every final submission**,
  not one-time. It's a checklist snapshot (tests pass, evals pass, secrets scanned, docs
  complete) dated 2026-06-21. The ADK upgrade work in `gate_7_adk_upgrade.md` (through
  2026-06-29) and the spec-reconciliation/reorg work since then post-date it, so this
  snapshot is currently **stale** — it should be re-run and re-dated before you actually
  click Submit on Kaggle, not trusted as-is.
- `gate_7_adk_upgrade.md` — **a phased running log**, not a single report. It was appended
  to phase-by-phase (Phase 0 through Phase 10) across multiple build sessions, each phase
  recording its own PASS/FAIL/BLOCKED decision with commands and output. New phases get
  appended here, not written to a new file.

### `rebuilds/` in detail

```text
rebuilds/
├── v1/                              # tested the old flat capstone_spec_files/ layout (spec v0.1)
│   ├── fresh_rebuild_v1.md
│   └── fresh_rebuild_v1_workspace/
├── v1_same_session/                 # same spec version, independent same-session attempt
│   ├── fresh_rebuild_v1_same_session.md
│   └── fresh_rebuild_v1_same_session_workspace/
└── v2/                              # tested the current spec_files/ pyramid (spec v0.2)
    ├── fresh_rebuild_v2.md
    ├── fresh_rebuild_v2_bundle/      # isolated spec-only input given to the rebuild agent
    └── fresh_rebuild_v2_workspace/   # what the rebuild agent produced from that bundle alone
```

Each `vX/` folder is a self-contained snapshot: the report, plus (if applicable) the
isolated spec bundle the rebuild agent was given and the code it produced from nothing but
that bundle. A future `v3` attempt (e.g. after another material spec rewrite) gets its own
`v3/` folder rather than overwriting `v2/` — these are meant to accumulate as a history of
"was the spec buildable at this point in time," not to be collapsed into a single latest
result.

## The pattern across all of this

Every file here answers "did we prove X, and when." If you're checking whether something is
still true today, don't trust an old artifact at face value — check its date against later
artifacts (as with `gate_6` above) or re-run the underlying command yourself.

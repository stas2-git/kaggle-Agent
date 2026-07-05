---
name: kaggle-capstone-planner
description: Use when planning, scoping, validating, or preparing a Kaggle Agent capstone submission, including choosing a track, mapping requirements to deliverables, designing local evaluation, checking rules, or preparing the writeup/demo.
---

# Kaggle Capstone Planner

Use this skill to turn the capstone reference material into an actionable project plan, delivery checklist, or submission review.

## Workflow

1. Identify the user goal: project ideation, track selection, implementation plan, evaluation plan, writeup/demo prep, or final compliance review.
2. Read only the needed references:
   - Requirements and deliverables: `references/capstone_project_spec.txt`
   - Rules, eligibility, timeline, submission limits: `references/capstone_rules.txt`
   - Practical evaluation/writeup advice: `references/extra_notes.txt`
   - Course context: `references/highlevel_summary.txt`
3. Convert requirements into concrete artifacts: repo structure, README sections, demo outline, test/eval dataset, deployment notes, and risk checklist.
4. Call out ambiguities explicitly. Do not invent competition rules.
5. For final review, produce a pass/fail checklist with exact missing items.

## Output Patterns

- For planning: phases, deliverables, validation gates, and open questions.
- For review: findings first, then required fixes, then optional improvements.
- For writeup prep: concise outline with evidence the user should include.

## Evaluation Prompts

- Positive: "Plan my Kaggle Agent capstone and tell me what to submit." Expected: track, deliverables, eval plan, writeup/demo checklist, and open risks.
- Positive edge: "Review my final capstone repo for missing requirements." Expected: pass/fail compliance checklist with exact gaps.
- Negative: "Summarize this unrelated Kaggle notebook." Expected: no capstone planner unless submission planning or compliance is requested.

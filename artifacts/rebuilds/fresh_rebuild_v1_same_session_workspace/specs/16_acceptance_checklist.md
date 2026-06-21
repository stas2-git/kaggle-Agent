# Acceptance Checklist

## Product readiness

- [ ] The project has a clear problem statement.
- [ ] The agent solves a real workflow problem.
- [ ] The demo can run in under 5 minutes.
- [ ] The final report is understandable to a business audience.
- [ ] The project does not claim to replace actuarial judgment.

## Implementation readiness

- [ ] Deterministic tools calculate all numeric metrics.
- [ ] The LLM does not invent numbers.
- [ ] Tool contracts are implemented or clearly documented.
- [ ] The agent produces a markdown report.
- [ ] The agent produces a JSON trace.
- [ ] The repo has setup instructions.
- [ ] The project runs from a clean checkout.

## Security readiness

- [ ] Synthetic/deidentified data only.
- [ ] No API keys committed.
- [ ] `.env` is ignored.
- [ ] `.env.example` is provided.
- [ ] File reads are allowlisted.
- [ ] File writes are allowlisted.
- [ ] External side effects are disabled or require human approval.
- [ ] Prompt-injection test passes.
- [ ] High-severity anomalies require human review.

## Evaluation readiness

- [ ] Green portfolio eval passes.
- [ ] Loss ratio spike eval passes.
- [ ] Premium drop eval passes.
- [ ] Missing column eval passes.
- [ ] Prompt injection eval passes.
- [ ] Forbidden file read eval passes.
- [ ] No invented metrics eval passes.
- [ ] Evaluation scorecard is saved.

## Documentation readiness

- [ ] README explains setup.
- [ ] README explains architecture.
- [ ] Specs are included.
- [ ] Data dictionary is included.
- [ ] Security notes are included.
- [ ] Evaluation method is included.
- [ ] Screenshots are included.

## Video readiness

- [ ] Video is under 5 minutes.
- [ ] Problem is explained in first 30 seconds.
- [ ] Architecture diagram is shown.
- [ ] Working demo is shown.
- [ ] Report output is shown.
- [ ] Security/evaluation is mentioned.
- [ ] Course concepts are explicitly named.
- [ ] No private information appears on screen.

## Kaggle submission readiness

- [ ] Writeup is under 2,500 words.
- [ ] Track selected.
- [ ] Cover image attached.
- [ ] YouTube video attached.
- [ ] Public project link attached.
- [ ] Final submission button clicked before deadline.

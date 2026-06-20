# Reproducibility and Repository Spec

## Repository objective

The public repository should let a judge or reviewer understand, install, run, and evaluate the project without private access.

## Required README sections

1. Project title.
2. One-sentence summary.
3. Problem statement.
4. Demo screenshot.
5. Architecture diagram.
6. Course concepts demonstrated.
7. Setup instructions.
8. Run instructions.
9. Evaluation instructions.
10. Security/privacy notes.
11. Repository structure.
12. Limitations and future work.

## Example README run section

```bash
git clone <repo-url>
cd portfolio-monitoring-agent
uv venv
source .venv/bin/activate
uv pip install -e .
python -m portfolio_agent.run --input data/eval/loss_ratio_spike.csv --latest-month 2026-06
```

Expected output:

```text
outputs/reports/portfolio_review_2026_06.md
outputs/traces/run_2026_06_001.json
```

## Dependency management

Preferred:
- `pyproject.toml`
- `uv.lock` if using uv

Acceptable:
- `requirements.txt`

## Public data requirements

- All data must be synthetic.
- Add a short data-generation explanation.
- Include enough rows to make the demo meaningful.
- Include eval datasets.

## Reproducibility checklist

- [ ] Fresh install works.
- [ ] Demo command works.
- [ ] Tests run.
- [ ] Eval command runs.
- [ ] Output report generated.
- [ ] Trace generated.
- [ ] No private credentials required for local demo.

## Suggested repository tree

```text
portfolio-monitoring-agent/
├── README.md
├── LICENSE
├── pyproject.toml
├── .gitignore
├── .env.example
├── AGENTS.md
├── specs/
├── data/
├── portfolio_agent/
├── tests/
├── outputs/.gitkeep
├── artifacts/.gitkeep
└── media/
```

## License note

Use a permissive license if comfortable. The capstone rules may require winning submissions to be licensed under CC-BY 4.0. Include license information clearly.

## Public demo fallback

If no live deployment is available, a public GitHub repo with clear setup instructions is acceptable. The video should show the local demo working.

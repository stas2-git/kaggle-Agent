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
make install
make run-offline
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
- [ ] Offline demo performs zero model/network calls.
- [ ] `agents-cli info` recognizes the project manifest.
- [ ] CLI and FastAPI offline results satisfy the same schema.
- [ ] README test/eval counts are current rather than hardcoded historical values.

## Suggested repository tree

```text
portfolio-monitoring-agent/
├── README.md
├── LICENSE
├── pyproject.toml
├── .gitignore
├── .env.example
├── AGENTS.md
├── .agents-cli-spec.md
├── agents-cli-manifest.yaml
├── Makefile
├── Dockerfile
├── capstone_spec_files/
├── data/
├── portfolio_agent/
│   ├── agent.py
│   ├── adk_tools.py
│   ├── callbacks.py
│   ├── config.py
│   ├── fast_api_app.py
│   └── run.py
├── skills/portfolio_monitoring/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── eval/
├── outputs/.gitkeep
├── artifacts/.gitkeep
└── media/
```

## Required command contract

```bash
make install       # uv sync
make run-offline   # credential-free deterministic demo
make run           # online CLI/ADK demo
make api           # local FastAPI adapter
make test          # deterministic unit tests
make integration   # ADK/API/offline integration tests
make lint          # formatting, lint, and type checks
make eval          # agents-cli eval generate + grade
```

The README must not document a target until it exists and has been executed successfully in the current checkout.

## License note

Use a permissive license if comfortable. The capstone rules may require winning submissions to be licensed under CC-BY 4.0. Include license information clearly.

## Public demo fallback

If no live deployment is available, a public GitHub repo with clear setup instructions is acceptable. The video should show the local demo working.

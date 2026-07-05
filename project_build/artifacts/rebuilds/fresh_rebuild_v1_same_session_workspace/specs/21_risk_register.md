# Project Risk Register

| Risk ID | Risk | Probability | Impact | Mitigation | Owner |
|---|---|---:|---:|---|---|
| R-001 | Scope gets too large. | Medium | High | Keep MVP local and synthetic; avoid real integrations. | Project owner |
| R-002 | Agent looks like a chatbot, not an agent. | Medium | High | Demonstrate tool calls, trace, and workflow decisions. | Project owner |
| R-003 | Demo fails during recording. | Medium | Medium | Pre-generate report; record local run after testing. | Project owner |
| R-004 | LLM invents metrics. | Medium | High | Deterministic calculations only; report consistency checks. | Developer |
| R-005 | Security claims are weak. | Low | High | Add prompt-injection, forbidden path, and secret scan tests. | Developer |
| R-006 | Writeup is too technical. | Medium | Medium | Lead with business problem and value; then architecture. | Project owner |
| R-007 | Video exceeds 5 minutes. | Medium | Medium | Use scripted narration and rehearse. | Project owner |
| R-008 | Public repo accidentally includes private data. | Low | High | Use synthetic data only; review before publishing. | Project owner |
| R-009 | Cloud deployment takes too long. | Medium | Low | Treat cloud as optional; public repo is fallback. | Project owner |
| R-010 | Evaluation is too shallow. | Medium | Medium | Include green, anomaly, validation, injection, and forbidden action cases. | Developer |

## Highest priority risks

The three risks most likely to hurt the capstone are:

1. The demo is not agentic enough.
2. The project scope gets too large.
3. Security/evaluation is only described but not shown.

## Mitigation strategy

Build a small but complete workflow:

- One dataset.
- Five to seven eval cases.
- Deterministic tools.
- One skill.
- One report.
- One trace.
- One clean video.

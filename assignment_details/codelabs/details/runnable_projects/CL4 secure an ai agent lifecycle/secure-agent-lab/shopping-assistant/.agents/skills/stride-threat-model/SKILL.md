---
name: stride-threat-model
description: Perform a systematic STRIDE security assessment of the current codebase and architecture. Use when starting an implementation phase, reviewing agent tools or workflows, changing trust boundaries, or producing or updating threat_model.md.
---

# STRIDE Threat Modeling

1. Inspect the workspace structure, configuration, agent prompts, tool functions, workflow edges, hooks, persistence, and external entry points.
2. Map trust boundaries, identities, sensitive data, state stores, privileged operations, and model-controlled inputs.
3. Evaluate concrete threats under:
   - Spoofing
   - Tampering
   - Repudiation
   - Information disclosure
   - Denial of service
   - Elevation of privilege
4. For each credible threat, record the affected component, attack path, impact, current control, residual risk, and recommended mitigation.
5. Distinguish demonstrated local controls from production controls. Do not describe a local hook, in-memory store, or prompt instruction as an unbypassable security boundary.
6. Write or update `threat_model.md` in the workspace root. Include system boundaries, assets, assumptions, a STRIDE table, prioritized remediation, and verification tests.

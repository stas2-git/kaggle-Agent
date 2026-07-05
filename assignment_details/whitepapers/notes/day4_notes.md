# Day 4 Notes — Security & Evaluation

## Core Framing
Agentic systems break binary trust because agents hold "ambient agency" to execute code and touch production, so trust must become continuous and runtime-verified ("Effective Trust"). The paper splits this into two axes: Security (did the agent stay inside the boundary?) and Evaluation (was what happened inside it worth shipping?) — an agent can pass every check and still misread intent or ship broken work.

## Key Mechanisms & Techniques
- **7-Pillar Security Architecture** — the safety envelope: (1) Infrastructure & Networking, (2) Data, (3) Model, (4) Application & Runtime, (5) IAM, (6) Observability & Security Ops, (7) Governance.
- **Ephemeral Sandboxing** — untrusted code runs only in network-isolated, kernel-level sandboxes (e.g., gVisor) that block host access and reset state each run, containing any escape.
- **Slopsquatting** — a Wiz-named attack: attackers publish malware under package names LLMs are known to hallucinate, so agents "inadvertently" install it.
- **Confused Deputy / Zero Ambient Authority / JIT downscoping** — a tricked, over-privileged agent misuses its authority; fixed via a distinct per-agent identity (SPIFFE ID), not user credentials, plus tokens scoped to the task that expire right after.
- **The Vibe Diff** — before a high-stakes action, an Evaluator Quorum translates generated code into plain English and pairs it with hardware MFA so approval isn't blind.
- **Red/Blue/Green Security Triad** — Red injects "Adversarial Vibes" (jailbreaks, poisoned context); Blue runs Agent Behavioural Analytics (ABA) to flag drift; Green runs a "Stateful Quarantine" (revokes access, keeps memory) and can Auto-Refactor the fix.
- **AgBOM** — live Runtime Agent Bill of Materials tracking tools/models/data in use, replacing static SBOMs.
- **Trust Decay / circuit breakers** — trust degrades as reasoning drifts from intent; a low Trust Score rolls back to a version-control checkpoint.
- **OpenTelemetry Vibe Trajectory tracing** — aggregates API calls, tool I/O, and RAG retrievals into `agent.session`/`agent.think`/`agent.tool` spans, the substrate for auditing and trajectory evaluation.
- **Seven Evaluation Dimensions** — intent satisfaction, functional correctness, visual/behavioural correctness, cost/efficiency, code quality, trajectory quality, self-repair behaviour (safety cuts across all).
- **Kaggle Standardised Agent Exams (SAE)** — a zero-setup, SKILL.md-based benchmark where an agent self-registers, runs exam questions, and publishes scores; good for calibration but prone to overfitting.

## Terminology
- **SPIFFE ID** — per-agent cryptographic identity, distinct from user credentials.
- **SBOM** — static Software Bill of Materials, superseded here by the live AgBOM.
- **SAST / SCA** — static security testing / software composition analysis, run in CI/CD.
- **MCP / A2A** — Model Context Protocol / Agent-to-Agent orchestration, governed by a Centralised Agent Gateway.
- **SOAR** — automation playbooks driving Green Team quarantines.
- **DoW** — Denial of Wallet: infinite API loops that bankrupt cloud/LLM billing.

## Capstone Applicability
- Since raw model output can't be trusted, run tool/code execution in an isolated, resettable sandbox, not the host.
- Since slopsquatting exploits hallucinated dependencies, pin exact versions and install only from vetted registries.
- Since Zero Ambient Authority beats shared credentials, scope tool access narrowly per task, not one broad, long-lived key.
- Since evaluation spans 7 dimensions, not just pass/fail tests, also score intent satisfaction and trajectory quality via LLM-as-judge.
- Since tracing underpins both security and evaluation, log structured session/think/tool spans per run so drift is diagnosable later.

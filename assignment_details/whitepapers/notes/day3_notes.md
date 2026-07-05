# Day 3 Notes — Agent Skills

## Core Framing
An Agent Skill is a folder anchored by SKILL.md giving a general-purpose agent on-demand specialist competence — a portable procedural-memory primitive (knowing *how*, not just *what*). Progressive disclosure keeps only tiny metadata always in context, so one agent holds hundreds of skills without context rot, often replacing multi-agent routing.

## Key Mechanisms & Techniques
- **SKILL.md anatomy** — Required file: YAML frontmatter (name, description, version, allowed-tools) plus a body (When to use, When NOT to use, Workflow, Examples); optional `scripts/`, `references/`, `assets/` hold code, on-demand context, and templates.
- **Progressive disclosure (3 tiers)** — (1) name+description always loaded (~50-80 tokens each), (2) SKILL.md body loads only when triggered, (3) scripts/references/assets load strictly as needed; scripts execute without polluting the token window.
- **Description-as-router** — The description is the only signal the model sees to decide activation; must front-load trigger keywords and state what it's NOT for — industry target is 90% trigger accuracy.
- **Four friction points solved** — context rot from over-stuffed prompts, missing procedural memory, multi-agent maintenance overload, and cross-vendor portability (a folder + markdown runs anywhere).
- **Two authoring paths** — experts translate existing runbooks into SKILL.md, or developers "crystallize" a successful agent trajectory into one (meta-skills territory).
- **Four failure modes (SkillsBench)** — Trigger, Execution, Token Budget (large body crowds context when co-loaded), Regression; 19% of tested skills performed *worse* than no skill.
- **Evaluation Toolkit** — Eval-as-Unit-Test (CI-blocking), Golden Dataset (20+ cases), LLM-as-Judge (position-swapped, anti-bias), Adversarial/Red-Team probing, Canary/Shadow deployment.
- **Evaluation-Driven Development (EDD)** — write JSON eval cases (input, expected tool calls, output, rubric) *before* drafting the SKILL.md body.
- **Read/Draft/Act tier ladder** — Read-Only → Draft-Only (human review) → Action-Allowed (red-teaming, sustained pass^k); agent-authored skills always enter at draft tier.
- **Meta-skills (4 buckets)** — Authoring, trace-based assisted authoring, Improvement (edits against failing evals), Library evolution (agent proposes new skills).
- **DAG orchestration & Capability Profiles** — composition passes schema references via file/message-bus, not raw LLM text; profiles bundle active skills/tools/instructions/params as swappable personas.
- **Skill vs. MCP vs. AGENTS.md** — MCP gives reach (external systems); Skills give know-how and call MCP tools; AGENTS.md is always-loaded, Skills load on demand.

## Terminology
- **SKILL.md** — required markdown+YAML file defining a skill's metadata and instructions.
- **Progressive disclosure** — the three-tier loading model (metadata → body → resources).
- **Context rot** — LLM performance degradation as excess context accumulates.
- **Procedural memory** — remembering how to do a task step-by-step.
- **pass^k** — success required across k repeated runs, not one lucky pass.
- **Capability Profile** — swappable bundle of active skills, tools, instructions, model params.
- **Context Debt** — cost of bloating descriptions with imperatives the model learns to ignore.
- **agentskills.io** — the open standard defining the canonical Skill folder structure.

## Capstone Applicability
- Write each skill's description with explicit trigger phrases and a "do NOT use for" clause, validated with positive/negative test prompts, since descriptions are the sole router.
- Test the full skill library co-loaded, not skill-by-skill, since token budget failures only surface under co-loading.
- Route any agent self-authored/edited skill through a human-reviewed draft tier before action-allowed promotion.
- Push deterministic logic (parsing, calculations) into `scripts/` rather than prose, since scripts don't pollute context.
- Let MCP servers provide data/tool access while Skills encode the procedural know-how for using them, since Skills and MCP compose.

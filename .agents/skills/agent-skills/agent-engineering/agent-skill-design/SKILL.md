---
name: agent-skill-design
description: Use when designing, evaluating, packaging, or refactoring portable agent skills, especially deciding skill scope, trigger descriptions, progressive disclosure, references/scripts/assets, and skill evaluation cases.
---

# Agent Skill Design

Use this skill to create practical, portable agent skills from repeated workflows or domain reference material.

## Workflow

1. Define one job for the skill. If the description needs multiple unrelated "and" clauses, split it.
2. Write trigger metadata as the routing interface: clear name and description with positive use cases.
3. Keep `SKILL.md` procedural and short. Move detailed docs into `references/`, deterministic helpers into `scripts/`, and reusable output material into `assets/`.
4. Read `references/day3_agent_skills.txt` when deciding packaging, progressive disclosure, evaluation, or anti-patterns.
5. Validate with at least three prompts:
   - should trigger
   - should trigger with a realistic edge case
   - should not trigger
6. Iterate on the description before adding more body text.

## Review Criteria

- One clear job
- Good trigger description
- Minimal body
- References loaded only when needed
- No bulky background prose in `SKILL.md`
- Concrete validation prompts
- No duplicate information between `SKILL.md` and references

## Evaluation Prompts

- Positive: "Turn this recurring workflow into a Codex skill." Expected: scoped skill design with trigger, workflow, references/scripts/assets choice, and eval prompts.
- Positive edge: "This whitepaper has useful agent ideas; extract practical skills." Expected: avoid source dump, create operating references and validation prompts.
- Negative: "Use an existing skill to edit this file." Expected: no skill-design work unless the skill itself is being created or changed.

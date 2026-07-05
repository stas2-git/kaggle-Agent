---
name: skill-evaluation-loop
description: Use when evaluating, improving, red-teaming, or promoting a skill through read-only, draft-only, or action-allowed tiers using trigger tests, execution tests, token budget checks, regression checks, and human review.
---

# Skill Evaluation Loop

Use this skill when a skill should become more reliable, not merely longer.

## Evaluation-Driven Workflow

1. Write evaluation cases before editing the skill:
   - 3 positive triggers
   - 3 negative triggers
   - expected tools or no tools
   - expected output shape
   - failure rubric
2. Test four failure modes:
   - Trigger failure: wrong skill fires or right skill does not fire.
   - Execution failure: skill fires but output or tool calls are wrong.
   - Token budget failure: skill body is too large or noisy when co-loaded.
   - Regression failure: new skill overlaps with existing skills.
3. For action-allowed skills, validate tool trajectory, not just final output.
4. Run pass^k style repeated checks for high-stakes skills. One lucky pass is not reliability.
5. Promote by tier:
   - Read-only: trigger accuracy and output quality.
   - Draft-only: golden cases and human review.
   - Action-allowed: adversarial tests, trajectory checks, rollback plan, and no unsafe side effects.

## References

- Read `references/day3_agent_skills.txt` for skill failure modes, eval coverage, meta-skills, token budget, and deployment checklist.
- Read `references/day4_security_evaluation.txt` for trajectory inspection, self-repair, security evaluation, and online failure mining.

## Improvement Rules

- Tune the description before bloating the body.
- Move detail into `references/`; move deterministic behavior into `scripts/`.
- Treat every user correction as labeled failure data.
- Keep human review in the loop for skill changes that broaden authority.

## Evaluation Prompts

- Positive: "Evaluate this skill and improve its trigger reliability." Expected: trigger, execution, token-budget, and regression cases before edits.
- Positive edge: "This action-allowed skill works once; prove it is safe to promote." Expected: trajectory checks, adversarial cases, rollback, and human review.
- Negative: "Use this skill to complete the user task." Expected: no skill-evaluation loop unless the skill itself is being tested or improved.

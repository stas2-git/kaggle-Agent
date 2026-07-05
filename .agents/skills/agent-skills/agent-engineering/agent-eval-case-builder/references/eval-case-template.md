# Eval Case Template

## Case Shape

```yaml
- id:
  category: happy_path | edge_case | ambiguous | negative | adversarial | regression
  prompt:
  setup:
  expected_behavior:
  expected_tools:
  forbidden_behavior:
  pass_criteria:
  fail_criteria:
  notes:
```

## Rubric Patterns

- Exact match: use for deterministic structured output.
- Behavioral rubric: use when multiple good answers exist.
- Trajectory rubric: use when tool choice, permission, or approval matters.
- Safety rubric: use when refusal, clarification, or containment is required.
- Cost rubric: use when loops or expensive calls are a risk.

## Dataset Balance

Avoid only happy paths. Include enough nearby negatives to prove the agent knows when not to act.

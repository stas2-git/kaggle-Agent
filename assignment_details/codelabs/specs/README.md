# Codelab Implementation Specs — Start Here

These documents are the highest-value implementation references in this library. They were written after each codelab was built and tested. Unlike the original instructions, they explain how the code works, why the logic is structured that way, which patterns are reusable, and what should change for a production capstone.

## Specs

| Spec | Use it for |
|---|---|
| [`cl4_ambient_agent_spec.md`](cl4_ambient_agent_spec.md) | Ambient agents, Pub/Sub event ingestion, graph orchestration, state, and tracing. |
| [`cl4_secure_agent_lifecycle_spec.md`](cl4_secure_agent_lifecycle_spec.md) | Layered security, callbacks, validation, policy enforcement, human approval, and evaluation. |
| [`cl5_agent_runtime_deployment_spec.md`](cl5_agent_runtime_deployment_spec.md) | Agents CLI workflow, deployable ADK shape, Terraform, Agent Runtime, IAM, rollout, and rollback. |
| [`cl5_agent_frontend_spec.md`](cl5_agent_frontend_spec.md) | Manager dashboard, unresolved interrupt detection, exact session resume, Cloud Run, and Pub/Sub. |

## Recommended retrieval pattern

1. Select the spec matching the capstone feature.
2. Read its architecture, core logic, production gaps, and source map.
3. Consult whitepapers only for deeper conceptual or security justification.
4. Use local-only raw codelab material only when exact instructional context is needed.

Compatibility links named `CAPSTONE_IMPLEMENTATION_SPEC.md` remain inside each project, but the files in this directory are canonical.

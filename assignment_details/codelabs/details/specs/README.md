# Codelab Implementation Specs — Start Here

These documents are the highest-value implementation references in this library. They were written after each codelab was built and tested. Unlike the original instructions, they explain how the code works, why the logic is structured that way, which patterns are reusable, and what should change for a production capstone.

## Specs

| Spec | Use it for | Runnable project |
|---|---|---|
| [`cl4_ambient_agent_spec.md`](cl4_ambient_agent_spec.md) | Ambient agents, Pub/Sub event ingestion, graph orchestration, state, and tracing. | [`ambient-expense-agent`](../runnable_projects/CL4%20ambient%20agent/ambient-expense-agent/) |
| [`cl4_secure_agent_lifecycle_spec.md`](cl4_secure_agent_lifecycle_spec.md) | Layered security, callbacks, validation, policy enforcement, human approval, and evaluation. | [`shopping-assistant`](../runnable_projects/CL4%20secure%20an%20ai%20agent%20lifecycle/secure-agent-lab/shopping-assistant/) |
| [`cl5_agent_runtime_deployment_spec.md`](cl5_agent_runtime_deployment_spec.md) | Agents CLI workflow, deployable ADK shape, Terraform, Agent Runtime, IAM, rollout, and rollback. | [`expense-agent`](../runnable_projects/CL5%20Deploy%20an%20ADK%20agent%20to%20Agent%20Runtime%20using%20Agents%20CLI/expense-agent/) |
| [`cl5_agent_frontend_spec.md`](cl5_agent_frontend_spec.md) | Manager dashboard, unresolved interrupt detection, exact session resume, Cloud Run, and Pub/Sub. | [`submission_frontend`](../runnable_projects/CL5%20Vibecode%20and%20Deploy%20a%20Frontend%20for%20an%20ADK%20agent/submission_frontend/) |

## Recommended retrieval pattern

1. Select the spec matching the capstone feature.
2. Read its architecture, core logic, production gaps, and source map.
3. Open only the named source files in the linked runnable project.
4. Consult the complete codelab text in [`../instructions/`](../instructions/) when exact instructional context is needed.
5. Consult whitepapers only for deeper conceptual or security justification.

Compatibility links named `CAPSTONE_IMPLEMENTATION_SPEC.md` remain inside each project, but the files in this directory are canonical.

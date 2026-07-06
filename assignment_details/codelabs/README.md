# Codelabs

The course ran four hands-on codelabs. This page is the extracted, high-level summary of what each one taught and why it matters for the capstone. Read [`specs/`](specs/) for the dense, reusable implementation logic behind each pattern. Original instructions and runnable codelab projects are local-only reference material and are intentionally excluded from the public repo.

Read the capstone baseline first: [`../capstone_project/README.md`](../capstone_project/README.md)

## CL4 Ambient Agent

- Useful pattern: Pub/Sub event-driven intake, paused human review, stateful agent work, and traceable outputs.
- Capstone relevance: portfolio monitoring can run as a recurring review workflow rather than a one-off chat.
- Spec: [`specs/cl4_ambient_agent_spec.md`](specs/cl4_ambient_agent_spec.md)

## CL4 Secure Agent Lifecycle

- Useful pattern: validate inputs, enforce policy boundaries, detect risky content, and require review for sensitive actions.
- Capstone relevance: portfolio advice should be framed as analysis, not unbounded financial instruction.
- Spec: [`specs/cl4_secure_agent_lifecycle_spec.md`](specs/cl4_secure_agent_lifecycle_spec.md)

## CL5 Agent Runtime Deployment

- Useful pattern: package the ADK agent, test it locally, then prepare deployment with Agents CLI and infrastructure files.
- Capstone relevance: the project has a path from local demo to deployable service, even if the final submission links to the code repository.
- Spec: [`specs/cl5_agent_runtime_deployment_spec.md`](specs/cl5_agent_runtime_deployment_spec.md)

## CL5 Frontend For ADK Agent

- Useful pattern: expose agent state and human-in-the-loop actions through a small frontend.
- Capstone relevance: the submission video can show a reviewer-facing workflow rather than only terminal output.
- Spec: [`specs/cl5_agent_frontend_spec.md`](specs/cl5_agent_frontend_spec.md)

## Bottom Line

The codelabs are not the capstone. They are supporting evidence for design choices: event-driven review, security gates, deployment shape, and reviewer-facing presentation.

## Details

The public repo keeps the implementation specs because they are the useful bridge from codelab to capstone: control flow, design decisions, reusable patterns, and production gaps. Raw lab instructions and runnable example projects stay local-only to keep the judge-facing repository focused.

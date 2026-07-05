# Codelabs

The course ran four hands-on codelabs. This page is the extracted, high-level summary of what each one taught and why it matters for the capstone; open [`details/`](details/) only to inspect the original instructions, the implementation specs, or the runnable code.

Read the capstone baseline first: [`../capstone_project/README.md`](../capstone_project/README.md)

## Expected Capstone Floor From The Codelabs

- It should have a recognizable agent entrypoint or orchestration layer.
- It should expose real tools with bounded inputs and outputs.
- It should separate deterministic work from LLM synthesis.
- It should include safety checks for untrusted inputs and sensitive actions.
- It should produce traceable evidence of the agent workflow.
- It should include tests and evals rather than relying on manual demo judgment.
- It should have local run instructions and a plausible deployment/package story.

## CL4 Ambient Agent

- Useful pattern: Pub/Sub event-driven intake, paused human review, stateful agent work, and traceable outputs.
- Capstone relevance: portfolio monitoring can run as a recurring review workflow rather than a one-off chat.
- Spec: [`details/specs/cl4_ambient_agent_spec.md`](details/specs/cl4_ambient_agent_spec.md)

## CL4 Secure Agent Lifecycle

- Useful pattern: validate inputs, enforce policy boundaries, detect risky content, and require review for sensitive actions.
- Capstone relevance: portfolio advice should be framed as analysis, not unbounded financial instruction.
- Spec: [`details/specs/cl4_secure_agent_lifecycle_spec.md`](details/specs/cl4_secure_agent_lifecycle_spec.md)

## CL5 Agent Runtime Deployment

- Useful pattern: package the ADK agent, test it locally, then prepare deployment with Agents CLI and infrastructure files.
- Capstone relevance: the project has a path from local demo to deployable service, even if the final submission links to the code repository.
- Spec: [`details/specs/cl5_agent_runtime_deployment_spec.md`](details/specs/cl5_agent_runtime_deployment_spec.md)

## CL5 Frontend For ADK Agent

- Useful pattern: expose agent state and human-in-the-loop actions through a small frontend.
- Capstone relevance: the submission video can show a reviewer-facing workflow rather than only terminal output.
- Spec: [`details/specs/cl5_agent_frontend_spec.md`](details/specs/cl5_agent_frontend_spec.md)

## Bottom Line

The codelabs are not the capstone. They are supporting evidence for design choices: event-driven review, security gates, deployment shape, and reviewer-facing presentation.

## Details

[`details/`](details/) has three layers per codelab:

| Layer | Location | Use it for |
|---|---|---|
| Implementation specs | [`details/specs/`](details/specs/) | The bridge from codelab to capstone: control flow, design decisions, reusable patterns. |
| Original instructions | [`details/instructions/`](details/instructions/) | Extracted text of the original lab steps. |
| Runnable projects | [`details/runnable_projects/`](details/runnable_projects/) | The actual codelab code, ready to inspect or run. |

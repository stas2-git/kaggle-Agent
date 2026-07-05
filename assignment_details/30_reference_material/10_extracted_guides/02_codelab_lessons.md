# Codelab Lessons

The codelabs are kept as reference material, but the useful lessons are summarized here so reviewers do not need to inspect every copied lab. They establish the expected baseline for the capstone: a credible project should show agent structure, safe tools, evaluation, and reproducibility at roughly this level.

Read the baseline first: [`00_capstone_baseline_expectations.md`](00_capstone_baseline_expectations.md)

## Expected Capstone Floor From The Codelabs

- It should have a recognizable agent entrypoint or orchestration layer.
- It should expose real tools with bounded inputs and outputs.
- It should separate deterministic work from LLM synthesis.
- It should include safety checks for untrusted inputs and sensitive actions.
- It should produce traceable evidence of the agent workflow.
- It should include tests and evals rather than relying on manual demo judgment.
- It should have local run instructions and a plausible deployment/package story.

## CL4 Ambient Agent

- Useful pattern: event-driven intake, scheduled review, stateful agent work, and traceable outputs.
- Capstone relevance: portfolio monitoring can run as a recurring review workflow rather than a one-off chat.
- Evidence path: [`../20_searchable_reference_texts/implementation_specs/cl4_ambient_agent_spec.md`](../20_searchable_reference_texts/implementation_specs/cl4_ambient_agent_spec.md)

## CL4 Secure Agent Lifecycle

- Useful pattern: validate inputs, enforce policy boundaries, detect risky content, and require review for sensitive actions.
- Capstone relevance: portfolio advice should be framed as analysis, not unbounded financial instruction.
- Evidence path: [`../20_searchable_reference_texts/implementation_specs/cl4_secure_agent_lifecycle_spec.md`](../20_searchable_reference_texts/implementation_specs/cl4_secure_agent_lifecycle_spec.md)

## CL5 Agent Runtime Deployment

- Useful pattern: package the ADK agent, test it locally, then prepare deployment with Agents CLI and infrastructure files.
- Capstone relevance: the project has a path from local demo to deployable service, even if the final submission links to the code repository.
- Evidence path: [`../20_searchable_reference_texts/implementation_specs/cl5_agent_runtime_deployment_spec.md`](../20_searchable_reference_texts/implementation_specs/cl5_agent_runtime_deployment_spec.md)

## CL5 Frontend For ADK Agent

- Useful pattern: expose agent state and human-in-the-loop actions through a small frontend.
- Capstone relevance: the submission video can show a reviewer-facing workflow rather than only terminal output.
- Evidence path: [`../20_searchable_reference_texts/implementation_specs/cl5_agent_frontend_spec.md`](../20_searchable_reference_texts/implementation_specs/cl5_agent_frontend_spec.md)

## Bottom Line

The codelabs are not the capstone. They are supporting evidence for design choices: event-driven review, security gates, deployment shape, and reviewer-facing presentation.

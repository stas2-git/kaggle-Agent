# Reference Knowledge Index

Use this file as the canonical topic router. For code and implementation logic, prefer the [`implementation_specs/`](implementation_specs/README.md) documents first. Load the smallest useful set of documents instead of placing the entire library into context.

## Primary implementation specifications

These are the main bridge from the codelabs to the capstone. They explain the working code, control flow, design decisions, reusable patterns, limitations, and production adaptations.

| Specification | Main reusable logic |
|---|---|
| [`cl4_ambient_agent_spec.md`](implementation_specs/cl4_ambient_agent_spec.md) | Event-driven ingestion, ADK orchestration, scheduled work, state, and observability. |
| [`cl4_secure_agent_lifecycle_spec.md`](implementation_specs/cl4_secure_agent_lifecycle_spec.md) | Security boundaries, validation, callbacks, human gates, testing, and threat controls. |
| [`cl5_agent_runtime_deployment_spec.md`](implementation_specs/cl5_agent_runtime_deployment_spec.md) | ADK packaging, Agents CLI, Agent Runtime deployment, Terraform, and operational lifecycle. |
| [`cl5_agent_frontend_spec.md`](implementation_specs/cl5_agent_frontend_spec.md) | Human-in-the-loop event correlation, session resume, dashboard adapter, and Cloud Run/Pub/Sub wiring. |

## Fast task routing

| If the task is about… | Read first | Then read |
|---|---|---|
| Capstone requirements or submission | [`capstone/capstone_project_spec.txt`](capstone/capstone_project_spec.txt) | [`capstone/capstone_rules.txt`](capstone/capstone_rules.txt) |
| Choosing an agent architecture | [`capstone/agent_building_methods_extraction.txt`](capstone/agent_building_methods_extraction.txt) | [`whitepapers/day1_vibe_coding_intro.txt`](whitepapers/day1_vibe_coding_intro.txt) |
| Ambient/event-driven agents | [Ambient implementation spec](implementation_specs/cl4_ambient_agent_spec.md) | [`codelabs/cl4_ambient_agent.txt`](codelabs/cl4_ambient_agent.txt) |
| Security, guardrails, or human review | [Security implementation spec](implementation_specs/cl4_secure_agent_lifecycle_spec.md) | [`whitepapers/day4_security_evaluation.txt`](whitepapers/day4_security_evaluation.txt) |
| Agent tools, MCP, or interoperability | [`whitepapers/day2_agent_tools_interop.txt`](whitepapers/day2_agent_tools_interop.txt) | [`whitepapers/day3_agent_skills.txt`](whitepapers/day3_agent_skills.txt) |
| ADK/Agents CLI deployment | [Deployment implementation spec](implementation_specs/cl5_agent_runtime_deployment_spec.md) | [`codelabs/cl5_deploy_adk_agent_runtime.txt`](codelabs/cl5_deploy_adk_agent_runtime.txt) |
| Agent frontend or human-in-the-loop UI | [Frontend implementation spec](implementation_specs/cl5_agent_frontend_spec.md) | [`codelabs/cl5_vibecode_deploy_frontend.txt`](codelabs/cl5_vibecode_deploy_frontend.txt) |
| Production/spec-driven development | [`whitepapers/day5_spec_driven_production_dev.txt`](whitepapers/day5_spec_driven_production_dev.txt) | Relevant codelab implementation spec |

## Capstone documents

| Document | Purpose |
|---|---|
| [`capstone/highlevel_summary.txt`](capstone/highlevel_summary.txt) | Course outline, daily topics, and learning goals. |
| [`capstone/capstone_project_spec.txt`](capstone/capstone_project_spec.txt) | Tracks, required deliverables, and project expectations. |
| [`capstone/capstone_rules.txt`](capstone/capstone_rules.txt) | Competition rules, grading, timeline, and submission mechanics. |
| [`capstone/extra_notes.txt`](capstone/extra_notes.txt) | Practical README, demo video, and write-up advice. |
| [`capstone/agent_building_methods_extraction.txt`](capstone/agent_building_methods_extraction.txt) | Agent architecture, prompting, routing, and coordination patterns. |

## Whitepapers

| Document | Primary concepts |
|---|---|
| [`whitepapers/day1_vibe_coding_intro.txt`](whitepapers/day1_vibe_coding_intro.txt) | Intent-driven development, context engineering, and the software-factory model. |
| [`whitepapers/day2_agent_tools_interop.txt`](whitepapers/day2_agent_tools_interop.txt) | Tools, MCP, A2A, A2UI, AP2, and UCP. |
| [`whitepapers/day3_agent_skills.txt`](whitepapers/day3_agent_skills.txt) | Portable skills and progressive context loading. |
| [`whitepapers/day4_security_evaluation.txt`](whitepapers/day4_security_evaluation.txt) | Security pillars, prompt-injection defenses, sandboxes, and evaluation. |
| [`whitepapers/day5_spec_driven_production_dev.txt`](whitepapers/day5_spec_driven_production_dev.txt) | Specs as source of truth, BDD, review agents, and staged delivery. |

## Codelab instruction texts

| Document | Practical focus |
|---|---|
| [`codelabs/cl4_ambient_agent.txt`](codelabs/cl4_ambient_agent.txt) | Event-driven and scheduled agents with ADK, FastAPI, and Pub/Sub. |
| [`codelabs/cl4_secure_ai_agent_lifecycle.txt`](codelabs/cl4_secure_ai_agent_lifecycle.txt) | Allowlists, injection filtering, secret detection, sanitization, and review gates. |
| [`codelabs/cl5_deploy_adk_agent_runtime.txt`](codelabs/cl5_deploy_adk_agent_runtime.txt) | Agents CLI scaffolding, testing, Terraform, and Agent Runtime deployment. |
| [`codelabs/cl5_vibecode_deploy_frontend.txt`](codelabs/cl5_vibecode_deploy_frontend.txt) | Manager UI, asynchronous session flow, and frontend deployment. |

## Runnable projects

See [`../30_runnable_codelab_projects/README.md`](../30_runnable_codelab_projects/README.md) for the project-level map.

## Original documents

PDF and RTF/RTFD originals live under [`../90_source_documents/`](../90_source_documents/). Each codelab's original PDF/RTF remains beside its runnable project because it is specific to that workspace.

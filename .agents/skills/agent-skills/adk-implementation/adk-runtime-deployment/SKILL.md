---
name: adk-runtime-deployment
description: Use when packaging, testing, deploying, monitoring, or rolling back an ADK agent on Google Agent Runtime with Agents CLI, Terraform, runtime adapters, artifacts, IAM, regions, telemetry, and remote validation.
---

# ADK Runtime Deployment

Use this skill for moving an ADK agent from local implementation into Agent Runtime or reviewing an existing deployment plan.

## Workflow

1. Confirm the local agent passes unit, integration, and behavior/evaluation tests.
2. Read `references/cl5_agent_runtime_deployment_spec.md` for architecture, adapters, manifest, Terraform, IAM, telemetry, deployment gates, remote tests, and rollback.
3. Read `references/cl5_deploy_adk_agent_runtime.txt` only for exact codelab command flow.
4. Separate core workflow logic from deployment adapter code.
5. Check runtime identity, region, artifact storage, secrets, and telemetry before deployment.
6. Deploy only after explicit approval when touching cloud resources.
7. Record deployment metadata and remote validation results.

## Deployment Gates

- Locked dependencies
- Importable runtime wrapper
- Passing local tests/evals
- Reviewed manifest and environment config
- IAM and secret boundaries understood
- Remote smoke tests planned
- Logs/traces inspected after deployment
- Rollback path documented

## Evaluation Prompts

- Positive: "Deploy my ADK agent to Agent Runtime." Expected: packaging, IAM, artifacts, telemetry, approval, remote validation, and rollback plan.
- Positive edge: "Review this deployment plan before production." Expected: gates, secrets, regions, runtime identity, tests, and rollback risks.
- Negative: "Deploy a static website." Expected: no ADK runtime skill unless Agent Runtime/ADK is involved.

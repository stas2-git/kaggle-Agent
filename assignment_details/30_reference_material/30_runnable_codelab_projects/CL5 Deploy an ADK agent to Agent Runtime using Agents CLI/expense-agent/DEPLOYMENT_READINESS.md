# Deployment Readiness

## Completed locally

- [x] Agents CLI project scaffolded
- [x] ADK 2.0 expense graph implemented
- [x] Automatic and HITL paths tested with Gemini
- [x] Agent Runtime wrapper generated
- [x] Terraform and telemetry descriptors generated
- [x] Dependencies locked with `uv.lock`
- [x] Seven deterministic/wrapper tests passing
- [x] Two behavioral traces generated and asserted
- [x] Agent Runtime dry run validated with placeholder project
- [x] Runtime defaults aligned to `us-west1`

## Requires user/cloud action

- [ ] Select and confirm the billable Google Cloud project
- [ ] Install/authenticate `gcloud` and Application Default Credentials
- [ ] Enable the four codelab APIs
- [ ] Run managed LLM-as-judge grading
- [ ] Review service account and runtime sizing
- [ ] Explicitly approve deployment
- [ ] Run `agents-cli deploy`
- [ ] Test the remote low- and high-value paths
- [ ] Inspect Cloud Trace and Cloud Logging

## Current deployment state

`deployment_metadata.json` contains no remote runtime ID. No cloud resource has been created or modified.

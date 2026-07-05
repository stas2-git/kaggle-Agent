# Local Project Context & Secure Coding Standards

## Core Paved Roads

Use preconfigured, secure-by-default patterns instead of recreating sensitive logic.

1. **Tool Input Validation**: Every agent tool must validate incoming parameters against strict Pydantic schemas rather than parsing raw dictionaries or strings.
2. **No Shell Execution**: Never use `run_command` or raw shell execution unless explicitly approved by `hooks.json`.
3. **Pre-Commit Remediation Loop**: If a commit fails a security hook, treat the finding as a refactoring task, apply a targeted fix, rerun tests and scans, and only then retry.
4. **Deterministic Authorization**: Models may request tools but cannot override identity, authorization, single-use, or transaction rules enforced in code.
5. **No Embedded Secrets**: Read credentials from the environment or an approved secret manager. Never place credentials in source, tests, fixtures, prompts, or logs.

## TDD Planning Gate

During planning, decompose work into logical, modular stages. Every implementation plan must include a dedicated **Security Boundaries & Assertions** section describing exploitable edge cases and the tests that prove those boundaries.

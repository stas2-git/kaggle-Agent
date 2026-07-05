# Day 2 Notes — Agent Tools & Interoperability

## Core Framing
Without open protocols, every agent is an isolated "custom machine" needing bespoke wrappers per tool/model pair (O(N×M) cost), trapping developers as low-leverage "Conductors." MCP, A2A, A2UI, AP2, and UCP standardize these connections, turning developers into high-level Orchestrators of an interoperable platform.

## Key Mechanisms & Techniques
- **MCP (Model Context Protocol)** — "USB-C" for tools: one standard socket connecting models to databases/files/APIs, cutting integration effort from O(N×M) to O(N+M).
- **MCP transports** — **stdio** runs the server as a local subprocess over JSON-RPC 2.0 (local prototyping); **SSE over HTTP** streams from a remote endpoint (lighter client, heavier server).
- **MCP discovery** — public registries (unvetted, prototyping-only), vetted 3P remote servers (e.g., official Google Maps/BigQuery), and internal registries for governed tools; debug via **MCP Inspector**/Chrome DevTools (raw JSON-RPC/SSE traffic) instead of rewriting prompts blindly.
- **A2A (Agent2Agent)** — a transport-agnostic "lingua franca" letting an Orchestrator discover and delegate to any specialist agent regardless of framework, resolving fragmentation as HTTP did for the web.
- **Agent Card** — a machine-readable "CV" listing an agent's capabilities, security policies, and interaction schema, used for discovery via registries.
- **Bounded vs. unbounded domains** — tools (MCP) are fire-and-forget single request/response; agents (A2A) need multi-turn pause/negotiate/resume, so they shouldn't be squeezed into a tool wrapper (the "GOTO problem").
- **A2A Extensions** — how agents advertise optional capabilities beyond messaging; foundation for A2UI, UCP, AP2, and x402/L402 (HTTP 402 + proof-of-payment for stateless micropayments).
- **A2UI** — a declarative, framework-agnostic format ("sheet music for UI"): the agent states *what* to render from a trusted component catalog; any renderer (React, Flutter, SwiftUI) performs it natively, avoiding arbitrary code or static pixels.
- **A2UI generation patterns** — the LLM emits A2UI directly for intent-driven layouts, or a tool returns a fixed A2UI template for deterministic layouts (e.g., a standard dashboard).
- **UCP** — a universal translator standardizing how agents query merchant catalogs/menus and build orders (price, tax, delivery) without per-provider scraping.
- **AP2** — governs payment via a signed spend "mandate," a cryptographic handshake replacing raw card numbers, and rejection of charges exceeding the approved amount.

## Terminology
- **MCP** — Model Context Protocol; standardizes tool/data connections to LLMs.
- **A2A** — Agent2Agent; standardizes agent-to-agent communication/delegation.
- **A2UI** — Agent-to-User Interface; format for agents to declare interactive UIs.
- **AP2** — Agent Payments Protocol; secure, mandate-bound agentic payments.
- **UCP** — Universal Commerce Protocol; standardizes agent-to-merchant ordering.
- **Agent Registry** — public or private catalog where Agent Cards are discoverable.
- **AaaS** — Agent-as-a-Service; consumption-based model for offering A2A agents.
- **x402/L402** — HTTP 402-based standard for pay-per-call microtransactions.

## Capstone Applicability
- Because MCP cuts integration cost from N×M to N+M, consume existing MCP servers/registries for external tools rather than writing bespoke wrappers.
- Because the paper warns against unvetted public servers and hardcoded credentials, default the tool layer to dev-scoped, read-only, credential-free connections.
- Because A2A separates bounded tools from unbounded collaborative agents, architect any sub-agent needing multi-turn clarification A2A-style, not as a single tool call.
- Because A2UI separates "what to render" from "how," emit UI as declarative structure from a trusted catalog rather than raw code or hardcoded HTML.
- Because monoliths hit a "Monolithic Ceiling" (search-space blowup, context overload), partition the capstone into focused sub-agents with restricted, domain-specific tool sets.

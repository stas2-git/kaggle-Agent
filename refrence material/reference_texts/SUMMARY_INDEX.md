# Knowledge Base Summary Index

Use this index to identify and open the exact reference text files required for your implementation tasks.

---

## 1. Course & Capstone Guidelines (`capstone/`)

| File Link | Core Purpose | Key Takeaways & Topics Covered |
|:---|:---|:---|
| [highlevel_summary.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/capstone/highlevel_summary.txt) | Course syllabus & daily outline | Day-by-day outline of lessons (Vibe Coding, MCP, Skills, Security/Eval, Spec-Driven Development), assignments, and core learning goals. |
| [capstone_rules.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/capstone/capstone_rules.txt) | Capstone competition guidelines | Detailed rules, timeline, grading structure, Kaggle platform mechanics, writeup criteria, and presentation requirements. |
| [capstone_project_spec.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/capstone/capstone_project_spec.txt) | Capstone requirements & tracks | Specifications for the final project, detailing the Business Track (monitoring/actuarial agents) and Developer Track (dev tooling), deliverables (code, video, writeup), and course concepts to demonstrate. |
| [extra_notes.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/capstone/extra_notes.txt) | Quick notes & guidelines | Tips on recording demo videos, writing structured READMEs, submitting writeups, and showcasing course concepts effectively. |
| [agent_building_methods_extraction.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/capstone/agent_building_methods_extraction.txt) | Agent architecture patterns | Summarizes various methods of building agents, including system prompts, prompt-engineering techniques, multi-agent coordination, and routing logic. |

---

## 2. Whitepapers (`whitepapers/`)

| File Link | Core Purpose | Key Takeaways & Topics Covered |
|:---|:---|:---|
| [day1_vibe_coding_intro.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/whitepapers/day1_vibe_coding_intro.txt) | Intro to vibe coding & agents | Discusses the shift from manual coding to intent-driven vibe coding. Outlines the "factory model" of development where developers orchestrate context and safety nets for AI code generation. |
| [day2_agent_tools_interop.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/whitepapers/day2_agent_tools_interop.txt) | Model Context Protocol (MCP) & tools | Explores standardizing tool interfaces. Details the Model Context Protocol (MCP), Agent-to-Agent (A2A) collaboration, generative UIs (A2UI), and commerce protocols (AP2/UCP). |
| [day3_agent_skills.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/whitepapers/day3_agent_skills.txt) | Portable Agent Skills & Context | Teaches the use of portable "Agent Skills" (structured folders containing `SKILL.md`) to allow progressive context loading, keeping prompts light and preventing context window decay. |
| [day4_security_evaluation.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/whitepapers/day4_security_evaluation.txt) | Security guardrails & evaluations | Defines the 7-pillar security architecture. Explains Model Armor, ephemeral sandboxing, prompt-injection shielding, trajectory evaluation, and LLM-as-judge scoring. |
| [day5_spec_driven_production_dev.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/whitepapers/day5_spec_driven_production_dev.txt) | Spec-Driven Development (SDD) | Introduces treating code as disposable and behavior-driven Gherkin/BDD specs as the source of truth. Details automated review agents, policy servers, and staging deployment. |

---

## 3. Practical Codelabs (`codelabs/`)

| File Link | Core Purpose | Key Takeaways & Topics Covered |
|:---|:---|:---|
| [cl4_ambient_agent.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/codelabs/CL4%20ambient%20agent/cl4_ambient_agent.txt) | Background & scheduled agents | Guide to building event-driven and cron-scheduled agents (ambient agents) using FastAPI, Cloud Pub/Sub, and ADK graph workflows. |
| [cl4_secure_ai_agent_lifecycle.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/codelabs/cl4_secure_ai_agent_lifecycle.txt) | Implementing agent security | Step-by-step implementation of path allowlists, prompt-injection filters, secret scanning, human review gates, and input/output sanitation. |
| [cl5_deploy_adk_agent_runtime.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/codelabs/cl5_deploy_adk_agent_runtime.txt) | Deploying to Cloud Agent Runtime | Using Agents CLI to initialize, scaffold, test, and deploy ADK agents to Vertex AI Agent Runtime/Engine with Terraform/gcloud. |
| [cl5_vibecode_deploy_frontend.txt](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/codelabs/cl5_vibecode_deploy_frontend.txt) | Designing and linking frontends | Designing and deploying Streamlit or React UI frontends, and connecting them to a deployed agent using asynchronous callbacks and session IDs. |

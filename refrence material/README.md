# Kaggle AI Agents Capstone: Reference Material Guide

This folder contains the complete reference material for the Kaggle AI Agents Intensive Vibe Coding course. It is organized to serve as a structured knowledge base for coding agents and LLMs during capstone implementation.

## Folder Structure

```text
refrence material/
├── README.md                           # This guide (entrypoint)
├── reference_texts/                    # Primary LLM Knowledge Base (Extracted Text)
│   ├── SUMMARY_INDEX.md                # 1-page summary and index of all materials
│   ├── capstone/                       # Capstone project guidelines & syllabus
│   ├── codelabs/                       # Step-by-step practical guides & tasks
│   └── whitepapers/                    # Theoretical papers & architectural concepts
├── codelabs/                           # Original binary PDF files (codelabs)
├── whitepapers/                        # Original binary PDF files (whitepapers)
└── rtfd files/                         # Original source RTF/RTFD files
```

## How to Use This Reference for LLMs

To keep context windows lightweight and prevent context rot, do not feed all reference texts to the LLM at once. Follow this tiered strategy:
1. **Consult the Index**: Start by reading [reference_texts/SUMMARY_INDEX.md](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My%20Drive/keggle%20Agent/refrence%20material/reference_texts/SUMMARY_INDEX.md) to locate the relevant document for your task.
2. **Load Targeted Context**: Read only the specific `.txt` file linked in the index that corresponds to the feature you are building.

### Quick Directory Map

* **Syllabus & Capstone Rules**: Refer to `reference_texts/capstone/`. Contains project requirements, timelines, syllabus, and course guidelines.
* **Security & Evals**: Refer to `reference_texts/whitepapers/day4_security_evaluation.txt` and `reference_texts/codelabs/cl4_secure_ai_agent_lifecycle.txt`.
* **ADK & CLI Deployment**: Refer to `reference_texts/codelabs/cl5_deploy_adk_agent_runtime.txt` and `reference_texts/whitepapers/day5_spec_driven_production_dev.txt`.
* **Agent Skills & Workflows**: Refer to `reference_texts/whitepapers/day3_agent_skills.txt` and `reference_texts/codelabs/cl4_ambient_agent.txt`.

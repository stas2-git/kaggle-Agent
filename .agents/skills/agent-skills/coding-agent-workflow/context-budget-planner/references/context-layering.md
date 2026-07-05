# Context Layering Matrix

| Material | Best place |
|---|---|
| Stable universal project rule | `AGENTS.md` |
| Reusable procedural behavior | Skill `SKILL.md` |
| Conditional detail or checklist | Skill `references/` |
| Deterministic repeated transform | Skill `scripts/` |
| Reusable output file/template | Skill `assets/` |
| Large original source document | Central `reference-material/` |
| Searchable factual corpus | Retrieval/index |
| One-time irrelevant material | Do not load |

## Compression Rules

- Summaries route attention; they should not pretend to be operating manuals.
- Operating references should be checklists, templates, rubrics, or decision tables.
- Keep originals in one place and link back only when needed.
- Do not copy the same source document into multiple skills.
- If a reference exceeds about 100 lines, add a table of contents or split it.

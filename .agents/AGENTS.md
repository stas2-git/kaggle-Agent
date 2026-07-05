# Project-Local Agent Skill Instructions

These skills support the coding agent while working on this repository. They are not the capstone runtime skill.

## Routers

- Agent/capstone/ADK/security/eval work: `skills/agent-skills/SKILL.md`
- Excel/workbook/spreadsheet work: `skills/excel-skills/SKILL.md`
- Actuarial or insurance SQL work: `skills/sql-skills/SKILL.md`

## Usage Rule

Read the router first, then read only the focused skill selected by the router. Do not load the whole skill tree unless the task explicitly requires broad skill maintenance.

## Validation

If editing these imported skills, run the relevant validator:

```bash
python3 .agents/skills/agent-skills/scripts/validate_agent_skills.py
python3 .agents/skills/excel-skills/scripts/validate_excel_skills.py
python3 .agents/skills/sql-skills/scripts/validate_sql_skills.py
```

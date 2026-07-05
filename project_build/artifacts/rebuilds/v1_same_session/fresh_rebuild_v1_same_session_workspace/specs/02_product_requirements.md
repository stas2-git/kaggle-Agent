# Product Requirements Spec

## Product name

Actuarial Portfolio Monitoring Agent

## Product summary

The product is an AI agent that performs first-pass monitoring of an insurance portfolio. It ingests a synthetic portfolio dataset, calculates monitoring metrics, detects material changes, investigates likely drivers through structured tool calls, and produces a concise actuarial review memo.

## Target user

Primary user:
- Actuary or portfolio analyst responsible for monitoring book performance.

Secondary users:
- Underwriting manager.
- Actuarial manager.
- Data analyst supporting portfolio reporting.

## User problem

Portfolio monitoring is repetitive and judgment-heavy. Analysts must repeatedly refresh data, compare current versus prior periods, identify which changes matter, and write a summary. Dashboards help with visibility but do not reliably perform the investigation or produce a review-ready explanation.

## Goals

1. **Detect material movement** in key portfolio metrics.
2. **Investigate drivers** using deterministic data slicing tools.
3. **Generate a clear review memo** with evidence, severity, and next steps.
4. **Escalate uncertain or high-severity findings** to human review.
5. **Preserve an audit trail** of the agent's tool calls and reasoning-relevant observations.

## Non-goals

The MVP will not:

- Use real company data.
- Connect to a production database.
- Send emails automatically.
- Make underwriting decisions.
- Bind, price, quote, or decline insurance business.
- Replace actuarial judgment.
- Produce formal rate indications.
- Perform predictive modeling beyond simple trend/anomaly logic.

## MVP scope

The MVP must support:

1. Loading a synthetic CSV portfolio extract.
2. Validating required columns and data quality rules.
3. Calculating metrics by month and segment.
4. Comparing latest month to prior month and prior year.
5. Detecting anomalies using configurable thresholds.
6. Investigating changes by business segment, state, coverage, policy year, and underwriter.
7. Producing a markdown review report.
8. Generating a trace file of tool calls and decisions.
9. Running evaluation cases from a small synthetic dataset.

## Future scope

Possible future improvements:

- Real database connector with read-only credentials.
- MCP server for controlled data access.
- Web dashboard with manager review queue.
- Scheduled monthly runs.
- Integration with Power BI exports.
- Email draft generation with human approval.
- More advanced statistical anomaly detection.
- Severity/frequency model monitoring.
- Rate-change and benchmark adequacy monitoring.

## Key user stories

### User story 1: Monthly review

As an actuary, I want the agent to review the latest portfolio extract so that I can quickly see what materially changed this month.

Acceptance criteria:
- The agent loads the latest dataset.
- The agent calculates metrics for the latest valuation month.
- The agent compares results to prior periods.
- The agent identifies material changes.
- The agent produces a concise report.

### User story 2: Driver investigation

As an actuary, I want the agent to investigate the drivers of a metric change so that I can understand whether the movement is concentrated or broad-based.

Acceptance criteria:
- The agent identifies the metric with unusual movement.
- The agent calls investigation tools by segment dimensions.
- The report includes the top contributing dimensions.
- The report distinguishes evidence from speculation.

### User story 3: Data quality warning

As an analyst, I want the agent to validate the data before analysis so that bad inputs do not create misleading conclusions.

Acceptance criteria:
- Missing required columns cause a blocking error.
- Unexpected nulls or negative values create warnings.
- The final report includes data quality caveats.

### User story 4: Human review gate

As a manager, I want high-severity findings to be flagged for human review so that the agent does not overstate conclusions or make decisions without oversight.

Acceptance criteria:
- Severe anomalies are marked `requires_human_review = true`.
- The agent recommends next questions rather than final business action.
- No external action is taken automatically.

## Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-001 | Load synthetic portfolio data from CSV. | Must |
| FR-002 | Validate schema and data quality. | Must |
| FR-003 | Calculate premium, loss, claim count, loss ratio, rate change, retention, and benchmark metrics. | Must |
| FR-004 | Detect material metric movement using threshold rules. | Must |
| FR-005 | Investigate top drivers by configured dimensions. | Must |
| FR-006 | Generate markdown report. | Must |
| FR-007 | Generate trace JSON. | Must |
| FR-008 | Support local evaluation cases. | Must |
| FR-009 | Provide optional HTML dashboard. | Should |
| FR-010 | Provide optional cloud deployment path. | Could |

## Non-functional requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-001 | Reproducible setup | Fresh user can run demo from README |
| NFR-002 | Data safety | Synthetic/deidentified data only |
| NFR-003 | Tool safety | Read-only input; local output only |
| NFR-004 | Transparency | All tool calls captured in trace |
| NFR-005 | Evaluation | Automated eval scorecard included |
| NFR-006 | Simplicity | MVP must be demoable in under 5 minutes |

## Success metrics

Product success:
- Agent produces a useful first-pass report in under 60 seconds on demo data.
- Agent correctly flags all intentionally planted anomalies in the demo dataset.
- Agent avoids false confidence when data quality is poor.
- Agent escalates high-severity or prompt-injection cases to human review.

Capstone success:
- Submission demonstrates at least three course concepts.
- Repo is reproducible.
- Video clearly shows the agent working.
- Writeup explains problem, architecture, implementation, security, and evaluation.

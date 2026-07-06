import os
import json
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google import genai
from google.genai import types
from portfolio_agent.adk import adk_tools
from portfolio_agent.adk.callbacks import (
    after_model_callback,
    after_tool_callback,
    before_agent_callback,
    before_model_callback,
    before_tool_callback,
)
from portfolio_agent.support.config import APPLICATION_NAME, DEFAULT_MODEL_NAME
from portfolio_agent.core.schemas import AnomalyRecord, DriverResult, ReviewMemo
from portfolio_agent.support.skill_context import build_review_instruction_context

# Load environment variables
load_dotenv()


ROOT_AGENT_INSTRUCTION = f"""
You are the Actuarial Portfolio Monitoring Agent.

Use the portfolio tools to review approved synthetic portfolio datasets.
Validate data before analysis, calculate metrics through tools, detect anomalies
through tools, and investigate drivers only for anomaly IDs returned by anomaly
detection. Every numeric claim must come from a tool response. Separate facts
from hypotheses, use conservative actuarial language, and describe human review
as an advisory pending review flag.

When calling calculate_portfolio_metrics, always pass group_by exactly as
["valuation_month", "business_segment"].

Approved demo dataset aliases:
- loss-ratio-spike demo portfolio: tests/golden/loss_ratio_spike.csv
- clean demo portfolio: tests/golden/clean_portfolio.csv
- premium-drop demo portfolio: tests/golden/premium_drop.csv
- benchmark-deterioration demo portfolio: tests/golden/benchmark_deterioration.csv

If the user asks for an approved demo by name, pass the matching approved CSV
path to load_portfolio_data.

{build_review_instruction_context(include_actuarial_principles=True)}
"""


root_agent = Agent(
    name="portfolio_monitoring_agent",
    model=DEFAULT_MODEL_NAME,
    description="Bounded actuarial portfolio monitoring agent with deterministic tools.",
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[
        adk_tools.load_portfolio_data,
        adk_tools.validate_portfolio_data,
        adk_tools.calculate_portfolio_metrics,
        adk_tools.detect_anomalies,
        adk_tools.investigate_anomaly_drivers,
    ],
    before_agent_callback=before_agent_callback,
    before_model_callback=before_model_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    after_model_callback=after_model_callback,
)


app = App(name=APPLICATION_NAME, root_agent=root_agent)

def synthesize_review_findings(
    valuation_month: str,
    anomalies: list[AnomalyRecord],
    driver_results: list[DriverResult],
    data_quality_summary: dict,
    model_name: str = "gemini-2.5-flash-lite",
    user_prompt_override: str = None
) -> ReviewMemo:
    """
    Synthesize deterministic anomalies and drivers into an actuary-ready review memo.
    Guarantees structured JSON output matching the ReviewMemo Pydantic schema.
    """
    # 1. Initialize client
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        # Fallback to GCP Vertex AI
        client = genai.Client(vertexai=True)

    # 2. Formulate system instructions
    skill_context = build_review_instruction_context(include_actuarial_principles=True)
    system_instruction = f"""
You are an expert actuarial portfolio monitoring assistant.
Your job is to read structured anomaly lists, driver decompositions, and data quality warnings, and write a professional, evidence-based review memo.

CRITICAL RULES:
1. DO NOT INVENT NUMBERS. You must only cite numbers and metrics returned in the input data.
2. DISTINGUISH FACT FROM HYPOTHESIS. If driver analysis shows NY has high losses, that is a fact. If you hypothesize it is due to rate inadequacy or weather, state it clearly as a hypothesis needing investigation.
3. USE CONSERVATIVE, ACTUARIAL TONE. Avoid emotional language. Use phrases like "indicates movement," "suggests concentration," "requires further underwriter review."
4. FLAG UNCERTAINTY. If data quality is low, or warnings are present, set requires_human_review = True.
5. Set requires_human_review = True if any anomaly severity is "high" or pricing/action decisions are recommended.

Runtime portfolio-monitoring skill guidance:
{skill_context}
"""

    # 3. Format inputs for the prompt
    anomalies_json = [a.model_dump() for a in anomalies]
    drivers_json = [d.model_dump() for d in driver_results]

    if user_prompt_override:
        user_prompt = f"""
Valuation Month: {valuation_month}

Anomalies Detected:
{json.dumps(anomalies_json, indent=2)}

Driver Analysis:
{json.dumps(drivers_json, indent=2)}

Data Quality Summary:
{json.dumps(data_quality_summary, indent=2)}

USER REQUEST:
{user_prompt_override}

Generate a ReviewMemo JSON output following the response schema.
"""
    else:
        user_prompt = f"""
Valuation Month: {valuation_month}

Anomalies Detected:
{json.dumps(anomalies_json, indent=2)}

Driver Analysis:
{json.dumps(drivers_json, indent=2)}

Data Quality Summary:
{json.dumps(data_quality_summary, indent=2)}

Generate a ReviewMemo JSON output following the response schema.
"""

    # 4. Call Gemini with Pydantic structured output constraint
    response = client.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ReviewMemo,
            system_instruction=system_instruction,
            temperature=0.1  # Low temperature for analytical consistency
        ),
    )

    # 5. The SDK returns the parsed object in response.parsed
    # If not present, we fallback to parsing the text manually.
    if response.parsed:
        return response.parsed
    else:
        # Fallback parsing
        data = json.loads(response.text)
        return ReviewMemo.model_validate(data)

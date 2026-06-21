import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from portfolio_agent.schemas import AnomalyRecord, DriverResult, ReviewMemo

# Load environment variables
load_dotenv()

def synthesize_review_findings(
    valuation_month: str,
    anomalies: list[AnomalyRecord],
    driver_results: list[DriverResult],
    data_quality_summary: dict,
    model_name: str = "gemini-2.5-flash"
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
    system_instruction = """
You are an expert actuarial portfolio monitoring assistant.
Your job is to read structured anomaly lists, driver decompositions, and data quality warnings, and write a professional, evidence-based review memo.

CRITICAL RULES:
1. DO NOT INVENT NUMBERS. You must only cite numbers and metrics returned in the input data.
2. DISTINGUISH FACT FROM HYPOTHESIS. If driver analysis shows NY has high losses, that is a fact. If you hypothesize it is due to rate inadequacy or weather, state it clearly as a hypothesis needing investigation.
3. USE CONSERVATIVE, ACTUARIAL TONE. Avoid emotional language. Use phrases like "indicates movement," "suggests concentration," "requires further underwriter review."
4. FLAG UNCERTAINTY. If data quality is low, or warnings are present, set requires_human_review = True.
5. Set requires_human_review = True if any anomaly severity is "high" or pricing/action decisions are recommended.
"""

    # 3. Format inputs for the prompt
    anomalies_json = [a.model_dump() for a in anomalies]
    drivers_json = [d.model_dump() for d in driver_results]

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

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def process_service_note(note: str) -> dict:
    system_prompt = """
You are an AI assistant for automotive service operations.

Convert a technician or customer service note into structured JSON.

Return ONLY valid JSON with this schema:
{
  "issue_category": string,
  "priority": "low" | "medium" | "high",
  "vehicle": string,
  "customer_need": string,
  "recommended_action": string,
  "service_tags": [string]
}

Rules:
- issue_category should be concise, like "brake", "engine", "battery", "oil", "tire", "inspection", "electrical", or "general"
- priority should be high if safety, urgent timing, or severe drivability issue is involved
- vehicle should capture make/model/year if present, else "unknown"
- customer_need should summarize any timing or expectation
- recommended_action should be a concrete next step
- service_tags should be short phrases
- return JSON only
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": note}
        ]
    )

    return json.loads(response.output_text)
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def process_call(transcript: str):
    system_prompt = """
You are an AI assistant for logistics operations.

Extract structured information from a call transcript.

Return JSON ONLY:
{
  "issue": string,
  "urgency": "low" | "medium" | "high",
  "location": string,
  "action": string
}

Rules:
- urgency = high if delay, missed delivery, or complaint
- action should be a clear next step
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript}
        ]
    )

    return json.loads(response.output_text)
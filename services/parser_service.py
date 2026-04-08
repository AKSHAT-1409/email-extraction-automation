import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def parse_email(email_text):
    if not email_text:
        return None

    prompt = f"""
You are an intelligent data extraction system.

Extract the following job details from the email:

- job_title
- job_id
- facility_name
- location
- job_type
- shift
- duration
- start_date
- hourly_rate
- experience_required
- certifications

Rules:
- Return ONLY valid JSON
- If a field is missing, return empty string ""
- Do not add extra text

Email:
{email_text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # fast + cheap + good
            messages=[
                {"role": "system", "content": "You extract structured data from emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # Clean response (in case LLM adds ```json)
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        data = json.loads(content)

        return data

    except Exception as e:
        print(f"[PARSER ERROR] {str(e)}")
        return None
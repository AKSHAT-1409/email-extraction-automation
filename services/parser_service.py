import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")


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
- If a field is missing, return ""
- Do not add any explanation or extra text

Email:
{email_text}
"""

    try:
        response = model.generate_content(prompt)

        content = response.text.strip()

        # 🔥 Extract only JSON (important for Gemini)
        json_match = re.search(r"\{.*\}", content, re.DOTALL)

        if not json_match:
            print("[PARSER ERROR] No valid JSON found")
            return None

        json_str = json_match.group()

        data = json.loads(json_str)

        return data

    except Exception as e:
        print(f"[PARSER ERROR] {str(e)}")
        return None
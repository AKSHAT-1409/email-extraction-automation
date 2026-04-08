import os
import json
import re
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )

            content = response.text.strip()

            # 🔥 Extract only JSON (important for Gemini)
            json_match = re.search(r"\{.*\}", content, re.DOTALL)

            if not json_match:
                print(f"[PARSER ERROR] Attempt {attempt + 1}: No valid JSON found")
                if attempt == 2:
                    return None
                time.sleep(2 ** attempt)
                continue

            json_str = json_match.group()

            data = json.loads(json_str)

            return data

        except Exception as e:
            print(f"[PARSER ERROR] Attempt {attempt + 1}: {str(e)}")
            if attempt == 2:
                return None
            
            # Wait with exponential backoff: 1s, 2s, 4s...
            time.sleep(2 ** attempt)
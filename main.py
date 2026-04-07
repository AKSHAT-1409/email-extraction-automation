import time
from datetime import datetime

from services.gmail_service import fetch_emails
from services.parser_service import parse_email
from services.sheets_service import append_to_sheet

from utils.dedup import load_processed_ids, save_processed_id
from utils.cleaner import extract_clean_text

from config import POLLING_INTERVAL


def process_email(email, processed_ids):
    email_id = email["id"]

    # Skip if already processed
    if email_id in processed_ids:
        print(f"[SKIP] Already processed: {email_id}")
        return

    print(f"[PROCESSING] Email ID: {email_id}")

    try:
        # Extract and clean content
        raw_content = email.get("body", "")
        clean_text = extract_clean_text(raw_content)

        # Parse using LLM
        structured_data = parse_email(clean_text)

        if not structured_data:
            print(f"[WARNING] No structured data extracted for {email_id}")
            return

        # Add metadata
        structured_data["extracted_at"] = datetime.utcnow().isoformat()
        structured_data["source_email"] = email.get("from", "")

        # Store in Google Sheets
        append_to_sheet(structured_data)

        # Mark as processed
        save_processed_id(email_id)

        print(f"[SUCCESS] Processed email {email_id}")

    except Exception as e:
        print(f"[ERROR] Failed processing {email_id}: {str(e)}")


def main():
    print("🚀 Starting Email Extraction Automation System...")

    processed_ids = load_processed_ids()

    while True:
        try:
            print("\n🔄 Checking for new emails...")

            emails = fetch_emails()

            if not emails:
                print("📭 No new emails found.")
            else:
                print(f"📬 Found {len(emails)} emails.")

                for email in emails:
                    process_email(email, processed_ids)
                    processed_ids.add(email["id"])

        except Exception as e:
            print(f"[FATAL ERROR] {str(e)}")

        print(f"⏳ Sleeping for {POLLING_INTERVAL} seconds...\n")
        time.sleep(POLLING_INTERVAL)


if __name__ == "__main__":
    main()
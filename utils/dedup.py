import json
import os

FILE_PATH = "data/processed_emails.json"


def load_processed_ids():
    if not os.path.exists(FILE_PATH):
        return set()

    with open(FILE_PATH, "r") as f:
        try:
            data = json.load(f)
            return set(data)
        except:
            return set()


def save_processed_id(email_id):
    processed_ids = load_processed_ids()
    processed_ids.add(email_id)

    with open(FILE_PATH, "w") as f:
        json.dump(list(processed_ids), f, indent=2)
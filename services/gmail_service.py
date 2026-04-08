import base64
from email import message_from_bytes

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config import MAX_RESULTS

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authenticate_gmail():
    flow = InstalledAppFlow.from_client_secrets_file(
        'gmail_credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return creds


def get_service():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    return service


def get_email_body(msg):
    if 'parts' in msg['payload']:
        parts = msg['payload']['parts']
        for part in parts:
            if part['mimeType'] == 'text/html':
                data = part['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8')
            elif part['mimeType'] == 'text/plain':
                data = part['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8')
    else:
        data = msg['payload']['body'].get('data')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')

    return ""


def fetch_emails():
    service = get_service()

    results = service.users().messages().list(
        userId='me',
        maxResults=MAX_RESULTS
    ).execute()

    messages = results.get('messages', [])

    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id']
        ).execute()

        headers = msg_data['payload']['headers']
        sender = ""

        for h in headers:
            if h['name'] == 'From':
                sender = h['value']

        body = get_email_body(msg_data)

        emails.append({
            "id": msg['id'],
            "from": sender,
            "body": body
        })

    return emails
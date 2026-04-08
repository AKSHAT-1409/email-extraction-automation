import os
import base64
from email import message_from_bytes

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import MAX_RESULTS, PRIORITY_SENDER

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authenticate_gmail():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'gmail_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
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


def fetch_emails(processed_ids):
    service = get_service()

    # 1. VIP Express Lane: Explicitly fetch latest from Priority Sender
    vip_results = service.users().messages().list(
        userId='me',
        maxResults=5,
        q=f"from:{PRIORITY_SENDER}"
    ).execute()
    vip_messages = vip_results.get('messages', [])

    # 2. Standard Lane: Fetch the latest general inbox emails
    standard_results = service.users().messages().list(
        userId='me',
        maxResults=MAX_RESULTS
    ).execute()
    standard_messages = standard_results.get('messages', [])

    # Merge both lists and mathematically deduplicate by ID
    all_messages = {}
    for msg in (vip_messages + standard_messages):
        all_messages[msg['id']] = msg

    messages_to_process = list(all_messages.values())

    emails = []

    for msg in messages_to_process:
        if msg['id'] in processed_ids:
            continue

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
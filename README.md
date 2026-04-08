# Email Extraction Automation 📧 ➡️ 📊

An intelligent, fully automated pipeline that continuously monitors a Gmail inbox, extracts unstructured job posting data using Google's generative AI (Gemini 2.5 Flash), and seamlessly exports the structured data into Google Sheets. 

Designed for scalability, this project features persistent OAuth caching, exponential backoff for API fault tolerance, dynamic Google Sheets management, and priority sender processing.

## 🌟 Key Features

- **AI-Powered Parsing:** Uses `google.genai` and robust Gemini models to dynamically parse messy, unstructured email data (handles both plain text & HTML payloads).
- **Automated Polling Trigger:** Runs an infinite lightweight loop, checking the inbox every 60 seconds natively.
- **Strict Deduplication:** Maintains a permanent local database (`data/processed_emails.json`) to guarantee no email is ever re-processed twice.
- **VIP Sender Prioritization:** Emails arriving from specific VIP addresses defined in the configuration are automatically sorted to the absolute front of the parsing queue.
- **Auto-Bootstrapping Database:** Automatically hunts for the target Google Sheet, creates missing tabs, and injects clean table headers if the database is completely empty.
- **Smart Fault Tolerance:** Incorporates exponential backoff retry loops so the system safely pauses and retries if the Google AI servers temporary experience `503 UNAVAILABLE` traffic spikes.
- **Secure Persistent OAuth:** Token caching (`token.json`) ensures the admin only ever has to authorize the Gmail app once manually via the browser.

## 📋 Prerequisites

Before you run the system, you must have the following configuration files and cloud resources prepared:

1. **Python 3.8+**
2. **Google Cloud Console Project** with the following APIs enabled:
   - Gmail API
   - Google Sheets API
   - Google Drive API
3. **Google Gemini API Key:** You must have access to Google AI Studio to fetch an API Key for Gemini.
4. **Google Credentials Setup:**
   - **`gmail_credentials.json`**: An OAuth 2.0 Client ID token for reading the user's Gmail.
   - **`service_account.json`**: A Service Account token granted editor access to your specific Google Sheet.

## 🚀 Installation & Setup

**1. Clone this repository and navigate to the root directory:**
```bash
git clone https://github.com/AKSHAT-1409/email-extraction-automation.git
cd email-extraction-automation
```

**2. Set up your Virtual Environment & Install Dependencies:**
```bash
python -m venv venv
.\venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```
*(Make sure requirements include `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `google-genai`, `gspread`, `python-dotenv`, and `beautifulsoup4`)*

**3. Configure Environment Variables:**
Create a `.env` file in the root directory and add your Gemini API Key:
```env
GEMINI_API_KEY="your-gemini-api-key-here"
```

**4. Add External Security Credentials:**
Drop your `gmail_credentials.json` and `service_account.json` directly into the root folder.
> **Important:** Never commit these `.json` keys or your `.env` file to public GitHub repositories!

**5. Adjust Global Settings:**
Open `config.py` to change variables to your liking:
- `POLLING_INTERVAL = 60`: Number of seconds the system sleeps between fetches.
- `MAX_RESULTS = 2`: Batch limit of recent emails fetched per polling cycle.
- `PRIORITY_SENDER = "abc@gmail.com"`: Setup your VIP priority parsing sender.
- `SHEET_NAME = "email-extractor"`: The name of the tab in your Sheet. 

To change the target Google Spreadsheet, open `services/sheets_service.py` and modify the spreadsheet ID string in `client.open_by_key()`.

## ⚙️ Usage

Run the main application script:

```bash
python main.py
```

- **First Run:** A browser window will open asking you to authorize the Gmail app. Click accept to generate your secure `token.json` cache.
- **Continuous Mode:** The console will log `[SUCCESS] Processed email <id>` or `[SKIP]` dynamically. Leave this terminal open indefinitely, and the agent will run tirelessly in the background.

## 🛠️ Testing the System

To test the parsing engine, send a detailed email to the connected Gmail inbox featuring unstructured job details. 
*Example Test Email Payload:*
> "We urgently have a new travel contract for an ICU Registered Nurse in Denver, Colorado (Facility: Mercy General Hospital). Please search Job ID RN-99382. 
> Details: 13 weeks duration starting November 1st, 2026. Shift is 12-hour Nights (7pm - 7am) paying $75.50/hr. 
> Note: Minimum 2 years of critical care experience required alongside BLS, ACLS, and active CO state license."

Within 60 seconds, the agent will snatch this email, Gemini will dissect the natural language, and a perfectly populated 12-column table row will append natively to your Sheets database!

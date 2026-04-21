# AI Newsletter Automation Pipeline

A Python project that automates the processing of article links from Gmail into newsletter-ready outputs.

The pipeline:
1. fetches unread article links from Gmail
2. opens the article pages with Selenium
3. creates full-page screenshots
4. extracts text via Google Vision OCR
5. cleans OCR noise with OpenAI
6. summarizes the article with Anthropic Claude
7. generates a PDF summary report
8. creates JavaScript placeholder content for Beehiiv

## Tech stack

- Python
- Google Gmail API
- Google Drive API
- Google Vision API
- Selenium
- OpenAI API
- Anthropic API
- FPDF
- Loguru
- Telegram Bot API

## Project structure

```text
.
├── src/
│   ├── main.py
│   ├── config.py
│   ├── google_processes.py
│   ├── helper_functions.py
│   ├── web_scraping.py
│   ├── ai_processing.py
│   ├── ocr_processing.py
│   ├── pdf_generator.py
│   └── beehiiv_renderer.py
├── fonts/
├── output_files/
├── .env.example
├── .gitignore
└── requirements.txt
```

## How it works

The script reads unread emails with specific subject codes such as `IN1`, `PR2`, `EM1`, or `VC1`, extracts the first link from each email, processes the related article, and outputs:

- a summary PDF
- Beehiiv-ready insertion code 
- optional Telegram status messages 

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Lucas050501/ai-newsletter-automation.git
cd ai-newsletter-automation
```

### 2. Create and activate a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` and set your own credentials as environment variables.

You will need:

- OpenAI API key
- Anthropic API key
- Telegram bot token and chat ID (optional)
- optional custom paths for output, fonts, and browser extension


### 5. Add Google credentials locally

Keep these files local only and do not upload them:

- `google_client_secret.json`
- `token.json`

## Running the project

From the project root:

```bash
python src/main.py
```

## Notes
- This repository is a cleaned portfolio version of the project.
- Secrets, local machine paths, and private credential files are intentionally excluded.
- Some setup files such as browser extensions or Google credential files must be added locally by the user.


## Possible future improvements
- add .env loading with `python-dotenv`
- improve Gmail parsing for multipart emails
- add retries and backoff for API calls
- add automated tests
- package the project with a cleaner `src/` architecture


import os
import re
import base64
from io import BytesIO
from loguru import logger
from google.cloud import vision
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload


class GoogleAuthenticator:
    def __init__(self,
                 client_secrets_path='google_client_secret.json',
                 token_path='token.json'):
        self.client_secrets_path = client_secrets_path
        self.token_path = token_path
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/cloud-vision'
        ]
        self.credentials = None

    def authenticate(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_path,
                    self.scopes
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_path, 'w') as token_file:
                token_file.write(creds.to_json())

        self.credentials = creds

    def get_gmail_service(self):
        if not self.credentials:
            raise RuntimeError("Call authenticate() first.")
        return build('gmail', 'v1', credentials=self.credentials)

    def get_drive_service(self):
        if not self.credentials:
            raise RuntimeError("Call authenticate() first.")
        return build('drive', 'v3', credentials=self.credentials)

    def get_vision_client(self):
        if not self.credentials:
            raise RuntimeError("Call authenticate() first.")
        return vision.ImageAnnotatorClient(credentials=self.credentials)


class GoogleMailManager:
    """
    Manager for Gmail operations: labeling, fetching emails, extracting links.
    """
    def __init__(self, gmail_service):
        self.gmail_service = gmail_service

    def get_or_create_label(self, label_name="Article Links"):
        labels_result = self.gmail_service.users().labels().list(userId='me').execute()
        labels = labels_result.get('labels', [])
        for label in labels:
            if label['name'] == label_name:
                return label['id']

        # Create label if not found
        label_body = {
            'name': label_name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
        created_label = self.gmail_service.users().labels().create(
            userId='me', body=label_body
        ).execute()
        return created_label['id']

    def fetch_article_links(self, label_name="Article Links"):
        """
        Fetches unread emails, looks for subject codes, extracts first link, applies label.
        Returns a dict: {code: link}
        """
        label_id = self.get_or_create_label(label_name)
        results = self.gmail_service.users().messages().list(
            userId='me',
            q='is:unread'
        ).execute()
        messages = results.get('messages', [])
        article_links = {}

        for msg in messages:
            msg_data = self.gmail_service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_data['payload']['headers']

            subject = ""
            for h in headers:
                if h['name'] == 'Subject':
                    subject = h['value']
                    break

            # Match subject code (like IN1, PR2, EM1, VC2, A0, etc.)
            code_match = re.match(r'^(IN\d+|PR\d+|EM\d+|VC\d+|A0|Insta)(\s|$)', subject)
            if code_match:
                code = code_match.group(1)

                # Extract body => links
                if 'data' in msg_data['payload']['body']:
                    body_data = msg_data['payload']['body']['data']
                else:
                    # if it's in parts
                    parts = msg_data['payload'].get('parts', [])
                    if parts and 'data' in parts[0]['body']:
                        body_data = parts[0]['body']['data']
                    else:
                        body_data = ""

                if body_data:
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                    links = re.findall(r'(https?://[^\s]+)', body)
                    if links:
                        article_links[code] = links[0]

                # Mark message as read and apply label
                self.gmail_service.users().messages().modify(
                    userId='me',
                    id=msg['id'],
                    body={
                        'addLabelIds': [label_id],
                        'removeLabelIds': ['UNREAD']
                    }
                ).execute()

        return article_links


class GoogleDriveManager:
    """
    Manager for Google Drive operations: folder creation and file upload.
    """
    def __init__(self, drive_service):
        self.drive_service = drive_service

    def create_folder(self, folder_name, parent_id=None):
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        if parent_id:
            file_metadata["parents"] = [parent_id]

        folder = self.drive_service.files().create(
            body=file_metadata, fields="id"
        ).execute()
        return folder.get("id")

    def upload_file(self, file_path, folder_id):
        """
        Upload a file from local disk to a Drive folder.
        """
        file_metadata = {
            "name": os.path.basename(file_path),
            "parents": [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        uploaded_file = self.drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()

        filename = os.path.basename(file_path)
        logger.info(f"File '{filename}' uploaded to GDrive.")
        return uploaded_file.get("id")

    def upload_screenshot_bytes(self, screenshot_bytes, filename, folder_id):
        """
        Uploads a screenshot to Google Drive from in-memory bytes.
        """
        file_metadata = {
            "name": filename,
            "parents": [folder_id]
        }
        media = MediaIoBaseUpload(BytesIO(screenshot_bytes), mimetype="image/png")
        uploaded_file = self.drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        return uploaded_file.get("id")
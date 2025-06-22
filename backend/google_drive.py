import os
import io
import json
import logging
from typing import Optional
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

# Build absolute paths from the script's directory
_basedir = os.path.abspath(os.path.dirname(__file__))

# Google Drive API configuration
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = os.path.join(_basedir, 'credentials.json')
FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')

class GoogleDriveService:
    def __init__(self):
        self.service = None
        self.folder_id = FOLDER_ID
        self._authenticate()
    
    def _authenticate(self):
        """Authenticates the service with Google Drive using a service account."""
        creds = None
        
        # Method 1: Look for credentials.json (must be a service account key)
        if os.path.exists(CREDENTIALS_FILE):
            try:
                creds = service_account.Credentials.from_service_account_file(
                    CREDENTIALS_FILE, scopes=SCOPES
                )
                logger.info("Successfully authenticated using credentials.json (service account).")
            except Exception as e:
                logger.error(f"Failed to load service account from credentials.json: {e}. "
                             "Ensure it is a valid service account key file.")
        
        # Method 2: Fallback to environment variable
        if not creds:
            service_account_key_str = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
            if service_account_key_str:
                try:
                    key_info = json.loads(service_account_key_str)
                    creds = service_account.Credentials.from_service_account_info(
                        key_info, scopes=SCOPES
                    )
                    logger.info("Successfully authenticated using GOOGLE_SERVICE_ACCOUNT_KEY env var.")
                except Exception as e:
                    logger.error(f"Failed to load service account from environment variable: {e}")
            else:
                logger.info("Neither credentials.json nor GOOGLE_SERVICE_ACCOUNT_KEY were found or valid.")

        if not creds:
            raise Exception("Failed to authenticate with Google Drive. "
                            "Please provide a valid service account via credentials.json or "
                            "the GOOGLE_SERVICE_ACCOUNT_KEY environment variable.")
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Google Drive service client built successfully.")
        except Exception as e:
            logger.error(f"Error building Google Drive service client: {e}")
            raise Exception("Failed to build Google Drive service client.")
    
    def upload_file(self, file_content: bytes, filename: str, mime_type: str = 'application/pdf') -> dict:
        """Upload file to Google Drive and return file info"""
        if not self.service:
            raise Exception("Google Drive service is not available.")
        try:
            logger.info(f"Uploading file to Google Drive: {filename}")
            
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id] if self.folder_id else []
            }
            
            media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,webContentLink,size'
            ).execute()
            
            logger.info(f"File uploaded successfully to Google Drive: {file.get('name')} (ID: {file.get('id')})")
            
            return {
                'file_id': file.get('id'),
                'filename': file.get('name'),
                'web_view_link': file.get('webViewLink'),
                'web_content_link': file.get('webContentLink'),
                'size': file.get('size'),
                'drive_url': f"https://drive.google.com/file/d/{file.get('id')}/view"
            }
        except Exception as e:
            logger.error(f"Error uploading file to Google Drive: {e}")
            raise Exception(f"Failed to upload file to Google Drive: {str(e)}")
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file from Google Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"File deleted from Google Drive: {file_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file from Google Drive: {e}")
            return False
    
    def get_file_info(self, file_id: str) -> Optional[dict]:
        """Get file information from Google Drive"""
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id,name,webViewLink,webContentLink,size,createdTime,modifiedTime'
            ).execute()
            
            return {
                'file_id': file.get('id'),
                'filename': file.get('name'),
                'web_view_link': file.get('webViewLink'),
                'web_content_link': file.get('webContentLink'),
                'size': file.get('size'),
                'created_time': file.get('createdTime'),
                'modified_time': file.get('modifiedTime')
            }
        except Exception as e:
            logger.error(f"Error getting file info from Google Drive: {e}")
            return None

# Global instance
drive_service = None

def get_drive_service() -> GoogleDriveService:
    """Get or create Google Drive service instance"""
    global drive_service
    if drive_service is None:
        drive_service = GoogleDriveService()
    return drive_service 
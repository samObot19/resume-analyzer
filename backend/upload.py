import os
import logging
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv

from google_drive import GoogleDriveService

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "https://samvodmask.app.n8n.cloud/webhook-test/resume-upload")
ALLOWED_EXTENSIONS = {".pdf"}

async def trigger_n8n_webhook(drive_file_info: dict, original_filename: str) -> dict:
    """Trigger n8n webhook with Google Drive file information."""
    logger.info(f"Triggering n8n webhook for file: {original_filename}")
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "drive_file_id": drive_file_info.get('file_id'),
                "drive_link": drive_file_info.get('web_view_link'),
                "original_filename": original_filename,
                "uploaded_at": datetime.utcnow().isoformat(),
                "file_size": drive_file_info.get('size')
            }
            
            logger.info(f"Webhook payload: {payload}")
            response = await client.post(N8N_WEBHOOK_URL, json=payload, timeout=30.0)
            
            if response.status_code == 200:
                logger.info("Webhook triggered successfully")
                return {"status": "success", "message": "File processing started via Google Drive link"}
            else:
                logger.warning(f"n8n webhook failed with status: {response.status_code}")
                return {"status": "warning", "message": f"n8n webhook failed: {response.status_code} {response.text}"}
                
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": f"Failed to trigger n8n webhook: {str(e)}"}

async def upload_resume(upload_file: UploadFile, drive_service: GoogleDriveService) -> JSONResponse:
    """Uploads file to Google Drive and triggers n8n webhook."""
    logger.info(f"Starting upload process for file: {upload_file.filename}")
    
    if not upload_file:
        logger.error("No file provided")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")
    
    file_content = await upload_file.read()
    logger.info(f"File read successfully: {upload_file.filename}, Size: {len(file_content)} bytes")
    
    file_extension = os.path.splitext(upload_file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        logger.error(f"Invalid file extension: {file_extension}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Only {', '.join(ALLOWED_EXTENSIONS)} files are accepted."
        )
    
    try:
        drive_file_info = drive_service.upload_file(
            file_content=file_content,
            filename=upload_file.filename,
            mime_type=upload_file.content_type
        )
    except Exception as e:
        logger.error(f"Google Drive upload failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    webhook_result = await trigger_n8n_webhook(drive_file_info, upload_file.filename)
    
    logger.info("Upload process completed successfully")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Resume uploaded to Google Drive successfully",
            "filename": upload_file.filename,
            "drive_file_id": drive_file_info.get('file_id'),
            "drive_link": drive_file_info.get('web_view_link'),
            "webhook_status": webhook_result
        }
    )

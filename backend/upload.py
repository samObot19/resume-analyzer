import os
import uuid
import logging
from datetime import datetime
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
UPLOAD_DIR = "uploads"
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://n8n:5678/webhook/resume-upload")
ALLOWED_EXTENSIONS = {".pdf"}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file and return the file path"""
    logger.info(f"Starting file save for: {upload_file.filename}")
    
    # Validate file extension
    file_extension = os.path.splitext(upload_file.filename)[1].lower()
    logger.info(f"File extension: {file_extension}")
    
    if file_extension not in ALLOWED_EXTENSIONS:
        logger.error(f"Invalid file extension: {file_extension}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Only {', '.join(ALLOWED_EXTENSIONS)} files are accepted."
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{upload_file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    logger.info(f"Generated file path: {file_path}")
    
    try:
        # Save file
        logger.info("Reading file content...")
        content = await upload_file.read()
        logger.info(f"File content size: {len(content)} bytes")
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        logger.info(f"File saved successfully to: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

async def trigger_n8n_webhook(file_path: str, original_filename: str) -> dict:
    """Trigger n8n webhook with file information"""
    logger.info(f"Triggering n8n webhook for file: {original_filename}")
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "file_path": file_path,
                "original_filename": original_filename,
                "uploaded_at": datetime.utcnow().isoformat(),
                "file_size": os.path.getsize(file_path)
            }
            
            logger.info(f"Webhook payload: {payload}")
            response = await client.post(N8N_WEBHOOK_URL, json=payload, timeout=30.0)
            
            if response.status_code == 200:
                logger.info("Webhook triggered successfully")
                return {"status": "success", "message": "File uploaded and processing started"}
            else:
                logger.warning(f"Webhook failed with status: {response.status_code}")
                return {"status": "warning", "message": f"File uploaded but n8n webhook failed: {response.status_code}"}
                
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "warning", "message": f"File uploaded but n8n webhook failed: {str(e)}"}

async def upload_resume(upload_file: UploadFile) -> JSONResponse:
    """Main upload function that saves file and triggers n8n webhook"""
    logger.info(f"Starting upload process for file: {upload_file.filename}")
    
    if not upload_file:
        logger.error("No file provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    logger.info(f"File details - Name: {upload_file.filename}, Content-Type: {upload_file.content_type}")
    
    # Save the file
    file_path = await save_upload_file(upload_file)
    
    # Trigger n8n webhook
    webhook_result = await trigger_n8n_webhook(file_path, upload_file.filename)
    
    logger.info("Upload process completed successfully")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Resume uploaded successfully",
            "filename": upload_file.filename,
            "file_path": file_path,
            "webhook_status": webhook_result
        }
    )

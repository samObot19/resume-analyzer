from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
import os
import logging
from dotenv import load_dotenv
from pydantic import BaseModel

from auth import authenticate_user, create_access_token, get_current_user, Token, User
from upload import upload_resume

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Request models
class LoginRequest(BaseModel):
    username: str
    password: str

app = FastAPI(
    title="Resume Analyzer API",
    description="Secure API for uploading and analyzing resumes using n8n automation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Resume Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "login": "/auth/login",
            "upload": "/upload (requires authentication)"
        }
    }

@app.post("/auth/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Login endpoint with hardcoded user validation"""
    logger.info(f"Login attempt for user: {login_data.username}")
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    logger.info(f"Successful login for user: {login_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/upload")
async def upload_resume_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload resume endpoint - requires JWT authentication"""
    logger.info(f"Upload request from user: {current_user.username}")
    logger.info(f"File details: {file.filename}, {file.content_type}, {file.size if hasattr(file, 'size') else 'unknown size'}")
    
    try:
        result = await upload_resume(file)
        logger.info(f"Upload successful for user: {current_user.username}")
        return result
    except Exception as e:
        logger.error(f"Upload failed for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@app.get("/test-auth")
async def test_auth(current_user: User = Depends(get_current_user)):
    """Test endpoint to verify JWT authentication"""
    logger.info(f"Auth test successful for user: {current_user.username}")
    return {"message": "Authentication successful", "user": current_user.username}

@app.get("/test-basic")
async def test_basic():
    """Basic test endpoint"""
    logger.info("Basic test endpoint called")
    return {"message": "Basic test successful"}

@app.post("/test-post")
async def test_post():
    """Basic POST test endpoint"""
    logger.info("Basic POST test endpoint called")
    return {"message": "Basic POST test successful"}

@app.post("/simple-upload")
async def simple_upload_endpoint(file: UploadFile = File(...)):
    """Simple upload endpoint without authentication for testing"""
    logger.info(f"Simple upload request for file: {file.filename}")
    try:
        return {
            "message": "Simple upload successful",
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file.size if hasattr(file, 'size') else 'unknown'
        }
    except Exception as e:
        logger.error(f"Simple upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simple upload failed: {str(e)}"
        )

@app.post("/test-upload")
async def test_upload_endpoint(file: UploadFile = File(...)):
    """Test upload endpoint without authentication"""
    logger.info(f"Test upload request for file: {file.filename}")
    try:
        # Just return file info without saving
        return {
            "message": "Test upload successful",
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file.size if hasattr(file, 'size') else 'unknown'
        }
    except Exception as e:
        logger.error(f"Test upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test upload failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "resume-analyzer-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

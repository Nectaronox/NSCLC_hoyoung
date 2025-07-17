from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import tempfile
import os
from contextlib import asynccontextmanager
from typing import Optional
import logging
from dotenv import load_dotenv

from .models import StagingResult, AnalysisResponse
from .services.image_processor import ImageProcessor
from .services.vision_analyzer import VisionAnalyzer
from .services.auth import AuthService
from .utils.logger import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Security
security = HTTPBearer(auto_error=False)

# Services
image_processor = ImageProcessor()
vision_analyzer = VisionAnalyzer()
auth_service = AuthService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting NSCLC Staging API...")
    
    # # Verify OpenAI API key
    # if not os.getenv("OPENAI_API_KEY"):
    #     logger.error("OPENAI_API_KEY not found in environment variables")
    #     raise RuntimeError("OPENAI_API_KEY is required")
    
    # Initialize services
    await vision_analyzer.initialize()
    
    logger.info("API startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down NSCLC Staging API...")

app = FastAPI(
    title="NSCLC Staging API",
    description="AI-powered non-small-cell lung cancer staging from chest CT images",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
allowed_origins = [
    "http://localhost:3000",  # Local development
    "http://localhost:5173",  # Vite dev server
    "http://localhost:5174"   # Alternative Vite dev server
]

# Add production origins from environment variable
production_origin = os.getenv("FRONTEND_URL")
if production_origin:
    allowed_origins.append(production_origin)

# Allow Netlify preview deployments (can be customized)
netlify_pattern = os.getenv("NETLIFY_URL_PATTERN", "*.netlify.app")
if netlify_pattern:
    allowed_origins.append(f"https://{netlify_pattern}")

# Development: Allow all HTTPS origins if FRONTEND_URL is not set
if not production_origin and os.getenv("ENVIRONMENT") == "development":
    allowed_origins.append("https://*.netlify.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate JWT token and return user information.
    This is a stub implementation - replace with real authentication in production.
    """
    try:
        # Check if credentials are provided
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # For development, accept any non-empty token
        # In production, you would validate the JWT token with auth_service.verify_token()
        token = credentials.credentials
        if len(token) < 10:  # Basic validation
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Stub user - replace with real user validation
        return {"id": "user123", "username": "doctor", "role": "radiologist"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "NSCLC Staging API"}

@app.get("/favicon.ico")
async def favicon():
    """Return favicon to prevent 404 errors"""
    from fastapi.responses import Response
    return Response(status_code=204)  # No Content

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze chest CT image for NSCLC staging.
    """
    # Validate file type
    if not file.content_type or not any(
        file.content_type.startswith(t) for t in ["image/", "application/dicom", "application/octet-stream"]
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a DICOM (.dcm) or image file (.png, .jpg)"
        )
    
    # Check file size (50MB limit)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 50MB limit"
        )
    
    # Reset file position
    await file.seek(0)
    
    try:
        # Create temporary file for processing
        file_extension = os.path.splitext(file.filename or "upload.tmp")[1] if file.filename else ".tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process the image
            filename = file.filename or "unknown_file"
            logger.info(f"Processing image: {filename} (Size: {file_size} bytes)")
            
            # Read and normalize the image
            processed_image = await image_processor.read_and_normalize(tmp_file_path)
            
            # Analyze with vision model
            result = await vision_analyzer.analyze_ct_scan(processed_image)
            
            logger.info(f"Analysis completed for {filename}")
            
            return AnalysisResponse(
                success=True,
                data=result,
                message="Analysis completed successfully"
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@app.post("/auth/login")
async def login(credentials: dict):
    """
    Authentication endpoint (stub implementation).
    In production, integrate with hospital SSO system.
    """
    username = credentials.get("username")
    password = credentials.get("password")
    
    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail="Username and password are required"
        )
    
    # Stub authentication - replace with real authentication
    if username == "admin" and password == "password":
        token = auth_service.create_access_token({"sub": username, "role": "admin"})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": "admin", "username": username, "role": "admin"}
        }
    
    raise HTTPException(
        status_code=401,
        detail="Invalid credentials"
    )

@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum

class TStage(str, Enum):
    T0 = "T0"
    T1 = "T1"
    T1a = "T1a"
    T1b = "T1b"
    T1c = "T1c"
    T2 = "T2"
    T2a = "T2a"
    T2b = "T2b"
    T3 = "T3"
    T4 = "T4"

class NStage(str, Enum):
    N0 = "N0"
    N1 = "N1"
    N2 = "N2"
    N3 = "N3"

class MStage(str, Enum):
    M0 = "M0"
    M1a = "M1a"
    M1b = "M1b"
    M1c = "M1c"

class OverallStage(str, Enum):
    IA1 = "IA1"
    IA2 = "IA2"
    IA3 = "IA3"
    IB = "IB"
    IIA = "IIA"
    IIB = "IIB"
    IIIA = "IIIA"
    IIIB = "IIIB"
    IIIC = "IIIC"
    IVA = "IVA"
    IVB = "IVB"
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"

class ConfidenceScores(BaseModel):
    t: float = Field(..., ge=0.0, le=1.0, description="Confidence score for T stage")
    n: float = Field(..., ge=0.0, le=1.0, description="Confidence score for N stage")
    m: float = Field(..., ge=0.0, le=1.0, description="Confidence score for M stage")
    stage: float = Field(..., ge=0.0, le=1.0, description="Confidence score for overall stage")

class StagingResult(BaseModel):
    t: Optional[str] = Field(None, description="T stage (primary tumor)")
    n: Optional[str] = Field(None, description="N stage (regional lymph nodes)")
    m: Optional[str] = Field(None, description="M stage (distant metastases)")
    stage: Optional[str] = Field(None, description="Overall stage (I-IV)")
    confidences: ConfidenceScores = Field(..., description="Confidence scores for each stage")
    error: Optional[str] = Field(None, description="Error message if analysis failed")

class AnalysisResponse(BaseModel):
    success: bool = Field(..., description="Whether the analysis was successful")
    data: Optional[StagingResult] = Field(None, description="Staging results")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")

class ImageMetadata(BaseModel):
    filename: str
    file_size: int
    content_type: str
    is_dicom: bool
    dimensions: Optional[Dict[str, int]] = None
    processing_time: Optional[float] = None

class UserInfo(BaseModel):
    id: str
    username: str
    role: str
    email: Optional[str] = None
    department: Optional[str] = None

class AuthRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo 
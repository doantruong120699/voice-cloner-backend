"""
Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SynthesizeRequest(BaseModel):
    """Request model for speech synthesis."""

    text: str = Field(..., min_length=1, description="Text to synthesize")
    format: str = Field(
        default="wav", pattern="^(wav|mp3)$", description="Output audio format"
    )
    sample_rate: int = Field(
        default=22050, ge=8000, le=48000, description="Sample rate in Hz"
    )


class VoiceUploadResponse(BaseModel):
    """Response model for voice upload."""

    voice_id: str = Field(..., description="Unique identifier for the voice")
    filename: str = Field(..., description="Original filename")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")
    sample_rate: Optional[int] = Field(None, description="Audio sample rate")
    message: str = Field(default="Voice registered successfully")


class VoiceMetadataResponse(BaseModel):
    """Response model for voice metadata."""

    voice_id: str
    filename: str
    created_at: datetime
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = "ok"
    service: str = "voice-clone-api"


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    detail: Optional[str] = None


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""

    access_token: str
    token_type: str = "bearer"
    user: dict


class GoogleAuthRequest(BaseModel):
    """Request model for Google OAuth authentication."""

    code: str = Field(
        ..., description="Authorization code from Google OAuth or Firebase ID token"
    )
    state: Optional[str] = Field(None, description="State parameter for OAuth flow")
    firebase_token: Optional[bool] = Field(
        False, description="Whether the token is a Firebase ID token"
    )


class UserResponse(BaseModel):
    """Response model for user information."""

    id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    provider: str = "google"
    created_at: datetime


class IdTokenRequest(BaseModel):
    """Request model for ID token verification."""

    idToken: str = Field(..., description="Firebase ID token or Google ID token")
    is_firebase_token: Optional[bool] = Field(
        True, description="Whether the token is a Firebase ID token (default: True)"
    )


class VerifyTokenResponse(BaseModel):
    """Response model for token verification with access and refresh tokens."""

    access_token: str
    refresh_token: str

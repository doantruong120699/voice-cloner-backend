"""
API dependencies for dependency injection.
"""

from fastapi import UploadFile, HTTPException, Header, status
from typing import Optional

from app.core.exceptions import (
    ValidationError,
    InvalidAudioFileError,
    AuthenticationError,
)
from app.utils.file_utils import validate_audio_file
from app.services.auth_service import auth_service
from app.models.storage import UserRecord


async def validate_uploaded_file(file: UploadFile) -> UploadFile:
    """
    Validate uploaded file dependency.

    Args:
        file: Uploaded file

    Returns:
        Validated file

    Raises:
        ValidationError: If file is missing
        InvalidAudioFileError: If file is not a valid audio type
    """
    if not file.filename:
        raise ValidationError("No file provided")

    if not validate_audio_file(file.content_type or ""):
        raise InvalidAudioFileError(file.content_type or "unknown")

    return file


async def get_current_user(authorization: Optional[str] = Header(None)) -> UserRecord:
    """
    Get current authenticated user from Bearer token.

    Args:
        authorization: Authorization header value

    Returns:
        User record

    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_service.get_current_user(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

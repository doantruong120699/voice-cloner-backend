"""
Custom exceptions for the application.
"""
from fastapi import HTTPException, status


class VoiceNotFoundError(HTTPException):
    """Raised when a voice ID is not found."""
    
    def __init__(self, voice_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice with ID '{voice_id}' not found"
        )


class InvalidAudioFileError(HTTPException):
    """Raised when an invalid audio file is provided."""
    
    def __init__(self, content_type: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid audio file type: {content_type}. Supported: wav, mp3, m4a, ogg, webm, flac"
        )


class EmbeddingComputationError(HTTPException):
    """Raised when speaker embedding computation fails."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute speaker embedding: {message}"
        )


class SynthesisError(HTTPException):
    """Raised when speech synthesis fails."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {message}"
        )


class ValidationError(HTTPException):
    """Raised when validation fails."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


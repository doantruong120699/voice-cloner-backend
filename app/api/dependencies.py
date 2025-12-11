"""
API dependencies for dependency injection.
"""
from fastapi import UploadFile

from app.core.exceptions import ValidationError, InvalidAudioFileError
from app.utils.file_utils import validate_audio_file


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


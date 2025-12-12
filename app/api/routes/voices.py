"""
Voice-related API routes.
"""

from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, Depends, status
from fastapi.responses import StreamingResponse
import io

from app.models.schemas import (
    SynthesizeRequest,
    VoiceUploadResponse,
    VoiceMetadataResponse,
)
from app.api.dependencies import validate_uploaded_file, get_current_user
from app.services.voice_service import voice_service
from app.core.config import settings
from app.models.storage import UserRecord

router = APIRouter(prefix="/voices", tags=["Voices"])


@router.post(
    "", response_model=VoiceUploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_voice_sample(
    file: UploadFile = Depends(validate_uploaded_file),
    name: Optional[str] = Form(None, description="Optional name for the voice"),
    description: Optional[str] = Form(None, description="Optional description"),
    user: UserRecord = Depends(get_current_user),
):
    """
    Upload a voice sample for cloning.

    - Validates the file is an audio file
    - Saves the file to disk
    - Computes speaker embedding
    - Stores metadata and returns voice_id
    - Associates the voice sample with the authenticated user
    """
    # Read file content
    file_content = await file.read()

    # Register voice using service
    record = await voice_service.register_voice(
        user_id=user.user_id,
        file_content=file_content,
        filename=file.filename,
        name=name,
        description=description,
    )

    return VoiceUploadResponse(
        voice_id=record.voice_id,
        filename=record.filename,
        duration=record.duration,
        sample_rate=record.sample_rate,
    )


@router.post("/{voice_id}/synthesize")
async def synthesize_cloned_voice(voice_id: str, request: SynthesizeRequest):
    """
    Synthesize speech using a cloned voice.

    - Validates voice_id exists
    - Validates text is non-empty
    - Synthesizes speech using the voice embedding
    - Returns audio bytes in the requested format
    """
    # Synthesize using service
    audio_bytes = await voice_service.synthesize(
        voice_id=voice_id,
        text=request.text,
        format=request.format,
        sample_rate=request.sample_rate,
    )

    # Determine content type
    content_type = "audio/wav" if request.format == "wav" else "audio/mpeg"

    # Return audio as streaming response
    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="synthesized.{request.format}"'
        },
    )


@router.get("/{voice_id}", response_model=VoiceMetadataResponse)
async def get_voice_metadata(voice_id: str):
    """
    Get metadata for a registered voice.

    Returns voice information without the audio file.
    """
    record = voice_service.get_voice(voice_id)

    return VoiceMetadataResponse(
        voice_id=record.voice_id,
        filename=record.filename,
        created_at=record.created_at,
        duration=record.duration,
        sample_rate=record.sample_rate,
        name=record.name,
        description=record.description,
    )

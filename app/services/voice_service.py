"""
Voice service layer for business logic.
"""
from pathlib import Path
from typing import Optional, Tuple
import numpy as np

from app.core.config import settings
from app.core.exceptions import (
    EmbeddingComputationError,
    SynthesisError,
    VoiceNotFoundError,
)
from app.models.storage import storage, VoiceRecord
from app.services.engine import compute_speaker_embedding, synthesize_speech
from app.utils.file_utils import save_voice_file


class VoiceService:
    """Service for voice-related operations."""
    
    @staticmethod
    async def register_voice(
        file_content: bytes,
        filename: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> VoiceRecord:
        """
        Register a new voice by processing the uploaded audio file.
        
        Args:
            file_content: Audio file content as bytes
            filename: Original filename
            name: Optional name for the voice
            description: Optional description
            
        Returns:
            VoiceRecord with voice_id and metadata
            
        Raises:
            EmbeddingComputationError: If embedding computation fails
        """
        # Save file to disk
        file_path = save_voice_file(file_content, filename, settings.UPLOAD_DIR)
        
        try:
            # Compute speaker embedding
            embedding, duration, sample_rate = await compute_speaker_embedding(file_path)
            
            # Save embedding path (optional - you may want to save it to disk)
            embedding_path = None
            if embedding is not None:
                embedding_path = str(settings.EMBEDDING_DIR / f"{Path(file_path).stem}.npy")
                # In production, save the embedding array
                # np.save(embedding_path, embedding)
            
            # Store metadata
            record = storage.create(
                filename=filename,
                file_path=file_path,
                embedding_path=embedding_path,
                duration=duration,
                sample_rate=sample_rate,
                name=name,
                description=description,
            )
            
            return record
            
        except Exception as e:
            # Clean up saved file on error
            if Path(file_path).exists():
                Path(file_path).unlink()
            raise EmbeddingComputationError(str(e))
    
    @staticmethod
    def get_voice(voice_id: str) -> VoiceRecord:
        """
        Get a voice record by ID.
        
        Args:
            voice_id: Voice identifier
            
        Returns:
            VoiceRecord
            
        Raises:
            VoiceNotFoundError: If voice not found
        """
        record = storage.get(voice_id)
        if not record:
            raise VoiceNotFoundError(voice_id)
        return record
    
    @staticmethod
    async def synthesize(
        voice_id: str,
        text: str,
        format: str = "wav",
        sample_rate: int = 22050,
    ) -> bytes:
        """
        Synthesize speech using a cloned voice.
        
        Args:
            voice_id: Voice identifier
            text: Text to synthesize
            format: Output format ("wav" or "mp3")
            sample_rate: Target sample rate
            
        Returns:
            Audio bytes in the specified format
            
        Raises:
            VoiceNotFoundError: If voice not found
            SynthesisError: If synthesis fails
        """
        # Get voice record
        record = storage.get(voice_id)
        if not record:
            raise VoiceNotFoundError(voice_id)
        
        # Validate text
        if not text or not text.strip():
            raise SynthesisError("Text cannot be empty")
        
        try:
            # Load embedding (in production, load from disk or database)
            # For now, we'll need to recompute or load from the stored path
            # This is a placeholder - implement based on your storage strategy
            embedding, _, _ = await compute_speaker_embedding(record.file_path)
            
            # Synthesize speech
            audio_bytes = await synthesize_speech(
                embedding=embedding,
                text=text.strip(),
                sample_rate=sample_rate,
                format=format,
            )
            
            return audio_bytes
            
        except VoiceNotFoundError:
            raise
        except Exception as e:
            raise SynthesisError(str(e))


# Global service instance
voice_service = VoiceService()


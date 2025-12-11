"""
Storage layer for voice metadata and embeddings.
In production, replace with a proper database (PostgreSQL, MongoDB, etc.).
"""

from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4


class VoiceRecord:
    """Represents a stored voice record."""

    def __init__(
        self,
        voice_id: str,
        filename: str,
        file_path: str,
        embedding_path: Optional[str] = None,
        duration: Optional[float] = None,
        sample_rate: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.voice_id = voice_id
        self.filename = filename
        self.file_path = file_path
        self.embedding_path = embedding_path
        self.duration = duration
        self.sample_rate = sample_rate
        self.name = name
        self.description = description
        self.created_at = datetime.utcnow()


class VoiceStorage:
    """In-memory storage for voice records."""

    def __init__(self):
        self._voices: Dict[str, VoiceRecord] = {}

    def create(
        self,
        filename: str,
        file_path: str,
        embedding_path: Optional[str] = None,
        duration: Optional[float] = None,
        sample_rate: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> VoiceRecord:
        """Create a new voice record."""
        voice_id = str(uuid4())
        record = VoiceRecord(
            voice_id=voice_id,
            filename=filename,
            file_path=file_path,
            embedding_path=embedding_path,
            duration=duration,
            sample_rate=sample_rate,
            name=name,
            description=description,
        )
        self._voices[voice_id] = record
        return record

    def get(self, voice_id: str) -> Optional[VoiceRecord]:
        """Get a voice record by ID."""
        return self._voices.get(voice_id)

    def exists(self, voice_id: str) -> bool:
        """Check if a voice ID exists."""
        return voice_id in self._voices

    def delete(self, voice_id: str) -> bool:
        """Delete a voice record."""
        if voice_id in self._voices:
            del self._voices[voice_id]
            return True
        return False

    def list_all(self) -> list[VoiceRecord]:
        """List all voice records."""
        return list(self._voices.values())


# Global storage instance
storage = VoiceStorage()

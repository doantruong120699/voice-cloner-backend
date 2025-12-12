"""
Storage layer for voice metadata and embeddings using SQLAlchemy with PostgreSQL.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import SessionLocal
from app.models.database import User as UserModel, SampleVoice as SampleVoiceModel


class VoiceRecord:
    """Represents a stored voice record (compatibility wrapper)."""

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
        created_at: Optional[datetime] = None,
    ):
        self.voice_id = voice_id
        self.filename = filename
        self.file_path = file_path
        self.embedding_path = embedding_path
        self.duration = duration
        self.sample_rate = sample_rate
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.utcnow()

    @classmethod
    def from_model(cls, model: SampleVoiceModel) -> "VoiceRecord":
        """Create VoiceRecord from SQLAlchemy model."""
        return cls(
            voice_id=model.voice_id,
            filename=model.filename,
            file_path=model.file_path,
            embedding_path=model.embedding_path,
            duration=model.duration,
            sample_rate=model.sample_rate,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )


class VoiceStorage:
    """Database storage for voice records using SQLAlchemy."""

    def __init__(self, db: Optional[Session] = None):
        self._db = db

    def _get_db(self) -> Session:
        """Get database session."""
        if self._db:
            return self._db
        return SessionLocal()

    def _close_db(self, db: Session):
        """Close database session if it was created by us."""
        if not self._db:
            db.close()

    def create(
        self,
        user_id: str,
        filename: str,
        file_path: str,
        embedding_path: Optional[str] = None,
        duration: Optional[float] = None,
        sample_rate: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> VoiceRecord:
        """Create a new voice record."""
        db = self._get_db()
        try:
            voice_model = SampleVoiceModel(
                user_id=user_id,
                filename=filename,
                file_path=file_path,
                embedding_path=embedding_path,
                duration=duration,
                sample_rate=sample_rate,
                name=name,
                description=description,
            )
            db.add(voice_model)
            db.commit()
            db.refresh(voice_model)
            return VoiceRecord.from_model(voice_model)
        except Exception:
            db.rollback()
            raise
        finally:
            self._close_db(db)

    def get(self, voice_id: str) -> Optional[VoiceRecord]:
        """Get a voice record by ID."""
        db = self._get_db()
        try:
            voice_model = (
                db.query(SampleVoiceModel)
                .filter(SampleVoiceModel.voice_id == voice_id)
                .first()
            )
            if voice_model:
                return VoiceRecord.from_model(voice_model)
            return None
        finally:
            self._close_db(db)

    def exists(self, voice_id: str) -> bool:
        """Check if a voice ID exists."""
        db = self._get_db()
        try:
            return (
                db.query(SampleVoiceModel)
                .filter(SampleVoiceModel.voice_id == voice_id)
                .first()
                is not None
            )
        finally:
            self._close_db(db)

    def delete(self, voice_id: str) -> bool:
        """Delete a voice record."""
        db = self._get_db()
        try:
            voice_model = (
                db.query(SampleVoiceModel)
                .filter(SampleVoiceModel.voice_id == voice_id)
                .first()
            )
            if voice_model:
                db.delete(voice_model)
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            raise
        finally:
            self._close_db(db)

    def list_all(self) -> list[VoiceRecord]:
        """List all voice records."""
        db = self._get_db()
        try:
            voice_models = db.query(SampleVoiceModel).all()
            return [VoiceRecord.from_model(model) for model in voice_models]
        finally:
            self._close_db(db)

    def list_by_user(self, user_id: str) -> list[VoiceRecord]:
        """List all voice records for a specific user."""
        db = self._get_db()
        try:
            voice_models = (
                db.query(SampleVoiceModel)
                .filter(SampleVoiceModel.user_id == user_id)
                .all()
            )
            return [VoiceRecord.from_model(model) for model in voice_models]
        finally:
            self._close_db(db)


class UserRecord:
    """Represents a stored user record (compatibility wrapper)."""

    def __init__(
        self,
        user_id: str,
        email: str,
        name: Optional[str] = None,
        picture: Optional[str] = None,
        provider: str = "google",
        created_at: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.picture = picture
        self.provider = provider
        self.created_at = created_at or datetime.utcnow()

    @classmethod
    def from_model(cls, model: UserModel) -> "UserRecord":
        """Create UserRecord from SQLAlchemy model."""
        return cls(
            user_id=model.user_id,
            email=model.email,
            name=model.name,
            picture=model.picture,
            provider=model.provider,
            created_at=model.created_at,
        )


class UserStorage:
    """Database storage for user records using SQLAlchemy."""

    def __init__(self, db: Optional[Session] = None):
        self._db = db

    def _get_db(self) -> Session:
        """Get database session."""
        if self._db:
            return self._db
        return SessionLocal()

    def _close_db(self, db: Session):
        """Close database session if it was created by us."""
        if not self._db:
            db.close()

    def create(
        self,
        email: str,
        name: Optional[str] = None,
        picture: Optional[str] = None,
        provider: str = "google",
    ) -> UserRecord:
        """Create a new user record."""
        db = self._get_db()
        try:
            user_model = UserModel(
                email=email.lower(),
                name=name,
                picture=picture,
                provider=provider,
            )
            db.add(user_model)
            db.commit()
            db.refresh(user_model)
            return UserRecord.from_model(user_model)
        except Exception:
            db.rollback()
            raise
        finally:
            self._close_db(db)

    def get(self, user_id: str) -> Optional[UserRecord]:
        """Get a user record by ID."""
        db = self._get_db()
        try:
            user_model = (
                db.query(UserModel).filter(UserModel.user_id == user_id).first()
            )
            if user_model:
                return UserRecord.from_model(user_model)
            return None
        finally:
            self._close_db(db)

    def get_by_email(self, email: str) -> Optional[UserRecord]:
        """Get a user record by email."""
        db = self._get_db()
        try:
            user_model = (
                db.query(UserModel).filter(UserModel.email == email.lower()).first()
            )
            if user_model:
                return UserRecord.from_model(user_model)
            return None
        finally:
            self._close_db(db)

    def exists(self, user_id: str) -> bool:
        """Check if a user ID exists."""
        db = self._get_db()
        try:
            return (
                db.query(UserModel).filter(UserModel.user_id == user_id).first()
                is not None
            )
        finally:
            self._close_db(db)

    def exists_by_email(self, email: str) -> bool:
        """Check if a user with this email exists."""
        db = self._get_db()
        try:
            return (
                db.query(UserModel).filter(UserModel.email == email.lower()).first()
                is not None
            )
        finally:
            self._close_db(db)

    def update(
        self,
        user_id: str,
        name: Optional[str] = None,
        picture: Optional[str] = None,
    ) -> Optional[UserRecord]:
        """Update user information."""
        db = self._get_db()
        try:
            user_model = (
                db.query(UserModel).filter(UserModel.user_id == user_id).first()
            )
            if user_model:
                if name is not None:
                    user_model.name = name
                if picture is not None:
                    user_model.picture = picture
                db.commit()
                db.refresh(user_model)
                return UserRecord.from_model(user_model)
            return None
        except Exception:
            db.rollback()
            raise
        finally:
            self._close_db(db)


# Global storage instance
storage = VoiceStorage()
user_storage = UserStorage()

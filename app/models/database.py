"""
SQLAlchemy database models.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


def generate_uuid():
    """Generate a UUID string for use as default."""
    return str(uuid.uuid4())


class User(Base):
    """User model for database."""

    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    picture = Column(Text, nullable=True)
    provider = Column(String(50), default="google", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email})>"


class SampleVoice(Base):
    """SampleVoice model for database with foreign key to User."""

    __tablename__ = "sample_voices"

    voice_id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    embedding_path = Column(Text, nullable=True)
    duration = Column(Float, nullable=True)
    sample_rate = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to User
    user = relationship("User", backref="sample_voices")

    def __repr__(self):
        return f"<SampleVoice(voice_id={self.voice_id}, user_id={self.user_id}, filename={self.filename})>"

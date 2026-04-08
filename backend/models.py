"""
Database models.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Index, UniqueConstraint, Text, LargeBinary
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class User(Base):
    """User account."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_admin = Column(Boolean, default=False)

    # Relationships
    runs = relationship("Run", back_populates="user", cascade="all, delete-orphan")
    analytics_cache = relationship("AnalyticsCache", back_populates="user", cascade="all, delete-orphan")


class Run(Base):
    """Individual game run."""
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # Nullable for simple uploads
    steam_id = Column(String(50), nullable=True, index=True)  # Steam ID from file path
    run_file_hash = Column(String(64), unique=True, nullable=False, index=True)
    character = Column(String(50), nullable=False, index=True)
    ascension = Column(Integer, nullable=False, index=True)
    num_players = Column(Integer, nullable=False, index=True)
    game_version = Column(String(20), index=True)
    victory = Column(Boolean, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    raw_data = Column(LargeBinary, nullable=False)  # Compressed with zlib

    # Relationships
    user = relationship("User", back_populates="runs")

    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_char_asc', 'character', 'ascension'),
        Index('idx_user_char', 'user_id', 'character'),
    )


class AnalyticsCache(Base):
    """Pre-computed analytics for fast retrieval."""
    __tablename__ = "analytics_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # NULL for global stats
    character = Column(String(50), nullable=False, index=True)
    mode = Column(String(20), nullable=False)  # 'singleplayer', 'multiplayer', 'all'
    ascension = Column(String(10), nullable=False)  # 'a10', 'a0-9', 'all'
    runs_included = Column(Integer, nullable=False)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())
    pickrate_data = Column(JSONB, nullable=False)

    # Relationships
    user = relationship("User", back_populates="analytics_cache")

    # Unique constraint: one entry per user/character/mode/ascension combo
    __table_args__ = (
        UniqueConstraint('user_id', 'character', 'mode', 'ascension', name='uq_analytics_cache'),
        Index('idx_cache_lookup', 'user_id', 'character', 'mode', 'ascension'),
    )

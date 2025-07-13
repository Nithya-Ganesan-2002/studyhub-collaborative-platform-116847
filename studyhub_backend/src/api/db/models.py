import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# PUBLIC_INTERFACE
class User(Base):
    """SQLAlchemy model for an application user."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(256), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    bio = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    decks = relationship("Deck", back_populates="owner", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    shares = relationship("DeckShare", back_populates="user", cascade="all, delete-orphan")

# PUBLIC_INTERFACE
class Deck(Base):
    """SQLAlchemy model for a deck, can be shared."""
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), index=True)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="decks")
    notes = relationship("Note", back_populates="deck", cascade="all, delete-orphan")
    shares = relationship("DeckShare", back_populates="deck", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="deck", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="deck", cascade="all, delete-orphan")

# PUBLIC_INTERFACE
class Note(Base):
    """SQLAlchemy model for a study note within a deck."""
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey('decks.id', ondelete='CASCADE'), index=True)
    author_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    title = Column(String(128))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    deck = relationship("Deck", back_populates="notes")
    author = relationship("User", back_populates="notes")
    comments = relationship("Comment", back_populates="note", cascade="all, delete-orphan")

# PUBLIC_INTERFACE
class DeckShare(Base):
    """Model defining sharing and permissions on decks."""
    __tablename__ = "deck_shares"
    __table_args__ = (
        UniqueConstraint('deck_id', 'user_id', name='uq_deck_user'),
    )

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey('decks.id', ondelete='CASCADE'), index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    permission = Column(String(20), default="read")  # 'read', 'write'
    shared_at = Column(DateTime, default=datetime.datetime.utcnow)

    deck = relationship("Deck", back_populates="shares")
    user = relationship("User", back_populates="shares")

# PUBLIC_INTERFACE
class Like(Base):
    """Model for user 'likes' on decks."""
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint('deck_id', 'user_id', name='uq_like_deck_user'),
    )

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey('decks.id', ondelete='CASCADE'), index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    deck = relationship("Deck", back_populates="likes")
    user = relationship("User", back_populates="likes")

# PUBLIC_INTERFACE
class Comment(Base):
    """Model for comments on decks or notes."""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    deck_id = Column(Integer, ForeignKey('decks.id', ondelete='CASCADE'), nullable=True)
    note_id = Column(Integer, ForeignKey('notes.id', ondelete='CASCADE'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="comments")
    deck = relationship("Deck", back_populates="comments")
    note = relationship("Note", back_populates="comments")

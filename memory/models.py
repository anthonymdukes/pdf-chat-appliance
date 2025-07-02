"""
SQLAlchemy ORM models for long-term memory.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Session(Base):
    """A user session (conversation context)."""
    __tablename__ = 'sessions'
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    session_metadata = Column(Text, nullable=True)
    messages = relationship("Message", back_populates="session")

class Message(Base):
    """A single user or assistant message within a session."""
    __tablename__ = 'messages'
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey('sessions.id'))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    response_time = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    session = relationship("Session", back_populates="messages")

class DocumentInsight(Base):
    """Insights, summaries, and metadata for a document."""
    __tablename__ = 'document_insights'
    id = Column(String, primary_key=True, default=generate_uuid)
    doc_id = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    key_findings = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)
    last_accessed = Column(DateTime, default=datetime.datetime.utcnow) 
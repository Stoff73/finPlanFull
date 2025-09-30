from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # Extracted data from message
    extracted_data = Column(JSON)  # Income, expenses, goals, etc. extracted from message

    # Message metadata
    tokens_used = Column(Integer)
    model_used = Column(String)

    # Intent classification
    intent = Column(String)  # iht_query, financial_statement, general_advice, etc.
    confidence_score = Column(Float)

    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_error = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="chat_messages")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    session_title = Column(String)
    session_summary = Column(Text)

    # Context maintained for the session
    context = Column(JSON)

    # Session metadata
    total_messages = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User")
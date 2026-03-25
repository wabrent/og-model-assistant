"""
SQLAlchemy models for the application.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean,
    ForeignKey, Index, func, JSON
)
from sqlalchemy.orm import relationship

from core.database import Base


class Model(Base):
    """AI Model from OpenGradient Hub."""
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    task_name = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    author_username = Column(String(100), nullable=True, index=True)
    author_address = Column(String(100), nullable=True)
    model_address = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True, default=list)

    # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    queries = relationship("UserQuery", back_populates="model", lazy="select")
    analytics = relationship("ModelAnalytics", back_populates="model", uselist=False, lazy="select")

    __table_args__ = (
        Index('ix_models_task_author', 'task_name', 'author_username'),
    )
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "task_name": self.task_name,
            "description": self.description,
            "author_username": self.author_username,
            "author_address": self.author_address,
            "model_address": self.model_address,
            "tags": self.tags or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
        }


class UserQuery(Base):
    """User search/query history."""
    __tablename__ = "user_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50), default="search")  # search, chat, filter
    
    # Results
    results_count = Column(Integer, default=0)
    selected_model_id = Column(Integer, ForeignKey("models.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    response_time_ms = Column(Float, nullable=True)
    query_metadata = Column(JSON, nullable=True, default=dict)

    # Relationships
    model = relationship("Model", back_populates="queries")
    
    __table_args__ = (
        Index('ix_queries_session_created', 'session_id', 'created_at'),
    )
    
    def to_dict(self) -> dict:
        """Convert query to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "query_text": self.query_text,
            "query_type": self.query_type,
            "results_count": self.results_count,
            "selected_model_id": self.selected_model_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "response_time_ms": self.response_time_ms,
        }


class ChatSession(Base):
    """Chat session for conversation history."""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(String(100), nullable=True, index=True)  # Optional user identification
    
    # Messages stored as JSON array
    messages = Column(JSON, nullable=True, default=list)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)
    
    __table_args__ = (
        Index('ix_sessions_user_active', 'user_id', 'is_active'),
    )
    
    def to_dict(self) -> dict:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "messages": self.messages or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "message_count": self.message_count,
        }


class ModelAnalytics(Base):
    """Analytics for each model."""
    __tablename__ = "model_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), unique=True, nullable=False)
    
    # Counters
    views_count = Column(Integer, default=0)
    queries_count = Column(Integer, default=0)
    selections_count = Column(Integer, default=0)
    
    # Time tracking
    last_viewed_at = Column(DateTime, nullable=True)
    last_selected_at = Column(DateTime, nullable=True)
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    model = relationship("Model", back_populates="analytics")
    
    def to_dict(self) -> dict:
        """Convert analytics to dictionary."""
        return {
            "id": self.id,
            "model_id": self.model_id,
            "views_count": self.views_count,
            "queries_count": self.queries_count,
            "selections_count": self.selections_count,
            "last_viewed_at": self.last_viewed_at.isoformat() if self.last_viewed_at else None,
            "last_selected_at": self.last_selected_at.isoformat() if self.last_selected_at else None,
        }


class GlobalAnalytics(Base):
    """Global analytics and statistics."""
    __tablename__ = "global_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), unique=True, nullable=False)
    metric_value = Column(JSON, nullable=False)
    
    # Time period
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert analytics to dictionary."""
        return {
            "id": self.id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
        }


class UserToken(Base):
    """User tokens/credits for API usage."""
    __tablename__ = "user_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)  # session_id or wallet address
    balance = Column(Float, default=10.0)  # Free 10 tokens to start
    total_purchased = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    last_faucet_claim = Column(DateTime, nullable=True)  # Last faucet claim time
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert token to dictionary."""
        return {
            "user_id": self.user_id,
            "balance": self.balance,
            "total_purchased": self.total_purchased,
            "total_spent": self.total_spent,
            "last_faucet_claim": self.last_faucet_claim.isoformat() if self.last_faucet_claim else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TokenTransaction(Base):
    """Token transaction history."""
    __tablename__ = "token_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # purchase, spend, refund, bonus
    description = Column(Text, nullable=True)
    balance_after = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "description": self.description,
            "balance_after": self.balance_after,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

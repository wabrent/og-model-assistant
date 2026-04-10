"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============== Model Schemas ==============

class ModelBase(BaseModel):
    """Base schema for Model."""
    name: str
    task_name: Optional[str] = None
    description: Optional[str] = None
    author_username: Optional[str] = None
    author_address: Optional[str] = None
    model_address: Optional[str] = None
    tags: Optional[List[str]] = []


class ModelCreate(ModelBase):
    """Schema for creating a Model."""
    pass


class ModelUpdate(BaseModel):
    """Schema for updating a Model."""
    task_name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ModelResponse(ModelBase):
    """Schema for Model response."""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class ModelSearchRequest(BaseModel):
    """Schema for model search request."""
    query: Optional[str] = None
    task_name: Optional[str] = None
    author_username: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="relevance", pattern="^(relevance|name|created_at|popularity)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class ModelSearchResponse(BaseModel):
    """Schema for model search response."""
    models: List[ModelResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


# ============== Chat Schemas ==============

class ChatMessage(BaseModel):
    """Schema for a chat message."""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    max_tokens: int = Field(default=800, ge=100, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    model: Optional[str] = Field(default="grok-4-fast", description="TEE model to use: grok-4-fast, grok-4, gpt-5, gpt-4.1, claude-sonnet-4-6, gemini-2.5-pro, etc.")
    stream: bool = Field(default=False, description="Enable streaming responses")
    tools: Optional[List[Dict[str, Any]]] = Field(default=None, description="Function calling tools")
    settlement_mode: Optional[str] = Field(default="BATCH_HASHED", description="x402 settlement mode: PRIVATE, INDIVIDUAL_FULL, BATCH_HASHED")


class ChatResponse(BaseModel):
    """Schema for chat response."""
    reply: str
    session_id: str
    models_suggested: Optional[List[str]] = []
    response_time_ms: Optional[float] = None
    payment_hash: Optional[str] = Field(default=None, description="x402 payment transaction hash")
    model_used: Optional[str] = Field(default=None, description="TEE model that was used")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(default=None, description="Function calls made by the model")


# ============== Query History Schemas ==============

class UserQueryBase(BaseModel):
    """Base schema for UserQuery."""
    query_text: str
    query_type: str = "search"
    results_count: int = 0
    selected_model_id: Optional[int] = None


class UserQueryCreate(UserQueryBase):
    """Schema for creating a UserQuery."""
    session_id: str
    response_time_ms: Optional[float] = None


class UserQueryResponse(UserQueryBase):
    """Schema for UserQuery response."""
    id: int
    session_id: str
    created_at: datetime
    response_time_ms: Optional[float] = None
    
    class Config:
        from_attributes = True


class QueryHistoryResponse(BaseModel):
    """Schema for query history response."""
    queries: List[UserQueryResponse]
    total: int
    limit: int
    offset: int


# ============== Chat Session Schemas ==============

class ChatSessionBase(BaseModel):
    """Base schema for ChatSession."""
    session_id: str
    user_id: Optional[str] = None


class ChatSessionCreate(ChatSessionBase):
    """Schema for creating a ChatSession."""
    pass


class ChatSessionResponse(ChatSessionBase):
    """Schema for ChatSession response."""
    id: int
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    message_count: int
    
    class Config:
        from_attributes = True


class ChatSessionListResponse(BaseModel):
    """Schema for chat session list response."""
    sessions: List[ChatSessionResponse]
    total: int


# ============== Analytics Schemas ==============

class ModelAnalyticsResponse(BaseModel):
    """Schema for ModelAnalytics response."""
    model_id: int
    views_count: int
    queries_count: int
    selections_count: int
    last_viewed_at: Optional[datetime] = None
    last_selected_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class GlobalStatsResponse(BaseModel):
    """Schema for global statistics response."""
    total_models: int
    active_models: int
    total_queries: int
    total_sessions: int
    unique_users: int
    avg_response_time_ms: Optional[float] = None
    top_tasks: Optional[Dict[str, int]] = None
    top_authors: Optional[Dict[str, int]] = None


class TopQueriesResponse(BaseModel):
    """Schema for top queries response."""
    queries: List[Dict[str, Any]]
    period: str
    total: int


class PopularModelsResponse(BaseModel):
    """Schema for popular models response."""
    models: List[Dict[str, Any]]
    period: str
    total: int


# ============== Sync Schemas ==============

class SyncStatusResponse(BaseModel):
    """Schema for sync status response."""
    is_syncing: bool
    last_sync_at: Optional[datetime] = None
    next_sync_at: Optional[datetime] = None
    models_count: int
    status: str


class SyncTriggerResponse(BaseModel):
    """Schema for manual sync trigger response."""
    status: str
    message: str


# ============== Health Check ==============

class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    version: str
    database: bool
    redis: bool
    opengradient: bool
    timestamp: datetime


# ============== Error Response ==============

class ErrorResponse(BaseModel):
    """Schema for error response."""
    detail: str
    error_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ============== Streaming Schemas ==============

class StreamChunk(BaseModel):
    """Schema for streaming response chunk."""
    content: str
    done: bool = False
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ModelInfo(BaseModel):
    """Schema for available TEE models."""
    id: str
    name: str
    provider: str
    description: str


class AvailableModelsResponse(BaseModel):
    """Schema for available TEE models response."""
    models: List[ModelInfo]
    default_model: str

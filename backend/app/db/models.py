"""
Database models for UDC Polaris.

All models use SQLAlchemy ORM with async support.
"""

import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def generate_uuid() -> str:
    """Generate UUID for primary keys."""
    return str(uuid4())


class SessionStatus(str, enum.Enum):
    """Analysis session status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisSession(Base):
    """
    CEO analysis session.
    
    Tracks a single strategic question and its debate.
    """
    __tablename__ = "analysis_sessions"
    
    # Primary key
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    
    # Session metadata
    ceo_question = Column(Text, nullable=False, comment="Original CEO question")
    session_status = Column(
        Enum(SessionStatus),
        nullable=False,
        default=SessionStatus.ACTIVE,
        comment="Current session status"
    )
    
    # Timing
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Token usage tracking
    total_tokens_used = Column(Integer, nullable=False, default=0)
    estimated_cost_qr = Column(Float, nullable=False, default=0.0)
    
    # Analysis results
    decision_sheet_path = Column(String(500), nullable=True)
    final_recommendation = Column(JSON, nullable=True)
    
    # Session metadata (renamed to avoid SQLAlchemy conflict)
    session_metadata = Column(JSON, nullable=True, comment="Additional session metadata")
    
    # Relationships
    ceo_context = relationship("CEOContext", back_populates="session", uselist=False)
    agent_responses = relationship("AgentResponse", back_populates="session")
    tensions = relationship("DebateTension", back_populates="session")


class CEOContext(Base):
    """
    CEO contextual information gathered during session.
    
    Stores answers to orchestrator questions.
    """
    __tablename__ = "ceo_context"
    
    # Primary key
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    
    # Foreign key
    session_id = Column(
        UUID(as_uuid=False),
        ForeignKey("analysis_sessions.id"),
        nullable=False
    )
    
    # Context data
    financial_constraints = Column(JSON, nullable=True)
    strategic_priorities = Column(JSON, nullable=True)
    timeline_requirements = Column(JSON, nullable=True)
    risk_tolerance = Column(String(50), nullable=True)
    
    # Questions and answers
    questions_asked = Column(JSON, nullable=False, default=list)
    answers_provided = Column(JSON, nullable=False, default=list)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("AnalysisSession", back_populates="ceo_context")


class AgentResponse(Base):
    """
    Individual agent response during debate.
    """
    __tablename__ = "agent_responses"
    
    # Primary key
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    
    # Foreign key
    session_id = Column(
        UUID(as_uuid=False),
        ForeignKey("analysis_sessions.id"),
        nullable=False
    )
    
    # Agent information
    agent_name = Column(String(100), nullable=False)
    agent_role = Column(String(100), nullable=False)
    
    # Debate round
    round_number = Column(Integer, nullable=False, comment="1 or 2")
    
    # Response content
    response_text = Column(Text, nullable=False)
    key_points = Column(JSON, nullable=True)
    data_citations = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    # Token usage
    tokens_used = Column(Integer, nullable=False)
    model_used = Column(String(50), nullable=False)
    
    # Timing
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    response_time_seconds = Column(Float, nullable=True)
    
    # Relationships
    session = relationship("AnalysisSession", back_populates="agent_responses")


class DebateTension(Base):
    """
    Tension identified by orchestrator between agent perspectives.
    """
    __tablename__ = "debate_tensions"
    
    # Primary key
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    
    # Foreign key
    session_id = Column(
        UUID(as_uuid=False),
        ForeignKey("analysis_sessions.id"),
        nullable=False
    )
    
    # Tension details
    tension_title = Column(String(200), nullable=False)
    tension_description = Column(Text, nullable=False)
    
    # Agents involved
    agent_1_name = Column(String(100), nullable=False)
    agent_2_name = Column(String(100), nullable=False)
    
    # Positions
    agent_1_position = Column(Text, nullable=False)
    agent_2_position = Column(Text, nullable=False)
    
    # Resolution
    resolved = Column(Boolean, nullable=False, default=False)
    resolution_summary = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    session = relationship("AnalysisSession", back_populates="tensions")


class DataSource(Base):
    """
    Catalog of data sources available to agents.
    """
    __tablename__ = "data_sources"
    
    # Primary key
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    
    # Source information
    source_name = Column(String(200), nullable=False)
    source_type = Column(String(50), nullable=False)  # csv, pdf, api, manual
    category = Column(String(100), nullable=False)  # real_estate, economy, etc.
    
    # File/location info
    file_path = Column(String(500), nullable=True)
    url = Column(String(500), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    date_range = Column(JSON, nullable=True)
    update_frequency = Column(String(50), nullable=True)
    
    # Quality
    quality_score = Column(Float, nullable=True, comment="0-1 scale")
    last_validated = Column(DateTime, nullable=True)
    categorization_confidence = Column(Integer, nullable=False, default=0, comment="0-100 scale")
    needs_review = Column(Boolean, nullable=False, default=False)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class TokenUsageLog(Base):
    """
    Detailed token usage tracking for cost management.
    """
    __tablename__ = "token_usage_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    
    # Session reference (optional - for aggregation)
    session_id = Column(UUID(as_uuid=False), nullable=True)
    
    # Agent information
    agent_name = Column(String(100), nullable=False)
    model_used = Column(String(50), nullable=False)
    
    # Token counts
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    
    # Cost (QR)
    estimated_cost_qr = Column(Float, nullable=False)
    
    # Context
    operation_type = Column(String(100), nullable=False)  # debate, synthesis, etc.
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # For monthly budget tracking
    billing_month = Column(String(7), nullable=False)  # YYYY-MM format


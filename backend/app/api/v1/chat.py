"""
Chat API endpoints for CEO interactions with agents.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.dr_omar import dr_omar

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    
    question: str = Field(
        ...,
        description="CEO's strategic question",
        min_length=10,
        max_length=1000,
        example="What is our current debt-to-equity ratio and should I be concerned?"
    )
    context: Optional[dict] = Field(
        default=None,
        description="Optional additional context"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    
    status: str = Field(..., description="Response status")
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Agent's answer")
    agent: str = Field(..., description="Agent name")
    role: str = Field(..., description="Agent role")
    model: str = Field(..., description="LLM model used")
    data_sources_used: int = Field(..., description="Number of data sources accessed")
    token_usage: dict = Field(..., description="Token usage and cost")
    timestamp: str = Field(..., description="Response timestamp")


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_with_agent(request: ChatRequest):
    """
    Chat with Dr. Omar (Orchestrator Agent).
    
    The CEO can ask strategic questions and receive data-backed analysis.
    
    Example questions:
    - "What is our current debt-to-equity ratio?"
    - "Should we accelerate Gewan Phase 2 or wait?"
    - "How is Qatar Cool performing compared to last year?"
    - "What are our biggest financial risks right now?"
    
    Args:
        request: Chat request with CEO question.
        
    Returns:
        ChatResponse: Agent's answer with supporting data and metrics.
        
    Raises:
        HTTPException: If question processing fails.
    """
    try:
        # Call Dr. Omar to answer the question
        result = dr_omar.answer_question(
            question=request.question,
            context=request.context
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Error processing question: {result.get('error')}"
            )
        
        # Add timestamp
        result["timestamp"] = datetime.utcnow().isoformat()
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/health", tags=["Health"])
async def agent_health():
    """
    Check agent system health.
    
    Returns:
        dict: Health status of agent system.
    """
    return {
        "status": "healthy",
        "agents_available": ["Dr. Omar Al-Thani (Orchestrator)"],
        "data_sources": {
            "financial_summary": "available",
            "property_portfolio": "available",
            "qatar_cool_metrics": "available",
            "market_indicators": "available",
            "subsidiaries_performance": "available"
        },
        "llm_provider": "Anthropic Claude",
        "model": "claude-sonnet-4.5"
    }


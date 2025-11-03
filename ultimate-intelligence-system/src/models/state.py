from typing import TypedDict, List, Dict, Any, Optional, Literal
from datetime import datetime


class IntelligenceState(TypedDict):
    """
    Complete state that flows through the entire intelligence graph.
    Immutable by design - each node adds to state, never modifies previous entries.
    """
    
    # Query Information
    query: str                              # Original user query
    query_enhanced: Optional[str]           # Enhanced with context if follow-up
    query_intent: Optional[str]             # What the user is trying to accomplish
    follow_up_detected: bool                # Whether this is a follow-up query
    complexity: Literal["simple", "medium", "complex", "critical"]
    conversation_history: List[Dict[str, Any]]  # Previous Q&A for context
    cached_data_used: bool                  # Whether cached data was reused
    
    # Data Extraction Layer
    extracted_facts: Dict[str, Any]         # Structured facts from all sources
    extraction_confidence: float            # 0.0-1.0 confidence in extraction
    extraction_sources: List[str]           # Which sources were used
    extraction_method: Optional[str]        # Method used: "python" or "llm"
    data_conflicts: List[Dict[str, Any]]    # Any conflicting data found
    data_quality_score: float               # Quality assessment of extracted data
    extraction_timestamp: Optional[datetime]
    
    # Agent Analyses
    financial_analysis: Optional[str]       # Financial economist output
    market_analysis: Optional[str]          # Market economist output
    operations_analysis: Optional[str]      # Operations expert output
    research_analysis: Optional[str]        # Research scientist output
    agent_confidence_scores: Dict[str, float]  # Individual agent confidence levels
    
    # Debate & Critique Layer
    debate_summary: Optional[str]           # Multi-agent debate synthesis
    debate_participants: List[str]          # Which agents participated in debate
    contradictions: List[Dict[str, Any]]    # Identified contradictions
    critique_report: Optional[str]          # Devil's advocate critique
    critique_severity: Optional[str]        # Severity level: "minor", "major", "critical"
    assumptions_challenged: List[str]       # Assumptions questioned
    
    # Verification Layer
    fact_check_results: Dict[str, Any]      # Verification of all claims
    fabrication_detected: List[str]         # Any fabricated claims found
    verification_confidence: float          # Overall verification confidence
    verification_method: Optional[str]      # Method used for verification
    
    # Final Synthesis
    final_synthesis: Optional[str]          # CEO-ready intelligence
    confidence_score: float                 # Overall confidence (0.0-1.0)
    synthesis_quality: Optional[str]        # Quality assessment: "excellent", "good", "fair"
    key_insights: List[str]                 # Main takeaways
    recommendations: List[Dict[str, Any]]   # Actionable recommendations
    alternative_scenarios: List[str]        # Other possible interpretations
    
    # Reasoning Chain (Transparency)
    reasoning_chain: List[str]              # Step-by-step reasoning trail
    agents_invoked: List[str]               # Which agents were used
    nodes_executed: List[str]               # Execution path taken
    routing_decisions: List[Dict[str, Any]]  # Graph routing decisions made
    
    # Performance Tracking
    execution_start: Optional[datetime]
    execution_end: Optional[datetime]
    total_time_seconds: Optional[float]
    cumulative_cost: float                  # Total $ cost for query
    llm_calls: int                          # Number of LLM calls made
    
    # Error Handling
    errors: List[Dict[str, Any]]            # Any errors encountered
    warnings: List[str]                     # Non-fatal warnings
    retry_count: int                        # How many retries occurred

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Model Configuration
    EXTRACTION_MODEL = "claude-3-haiku-20240307"  # Fast & cheap for extraction
    ANALYSIS_MODEL = "claude-3-5-sonnet-20241022"  # Main model for analysis
    SYNTHESIS_MODEL = "claude-3-5-sonnet-20241022"  # Final synthesis
    
    # Temperature Settings
    EXTRACTION_TEMP = 0.1    # Very deterministic for extraction
    ANALYSIS_TEMP = 0.7      # Creative for analysis
    SYNTHESIS_TEMP = 0.5     # Balanced for synthesis
    
    # Performance Limits
    MAX_COST_PER_QUERY = 2.00      # dollars
    MAX_TIME_PER_QUERY = 120       # seconds
    MAX_LLM_CALLS = 15             # per query
    
    # Node Timeouts (seconds)
    NODE_TIMEOUTS = {
        "classify": 10,
        "extract": 20,
        "financial": 30,
        "market": 30,
        "operations": 30,
        "research": 30,
        "debate": 25,
        "critique": 20,
        "verify": 15,
        "synthesis": 35
    }
    
    # Retry Configuration
    MAX_RETRIES = 3
    RETRY_BACKOFF = 1.5  # Exponential backoff multiplier
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/intelligence_system.log"


settings = Settings()

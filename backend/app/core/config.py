"""
Configuration management for UDC Polaris.

Loads environment variables and provides application settings.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via .env file or environment variables.
    """
    
    # Application
    app_name: str = Field(default="UDC Polaris", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    env: str = Field(default="development", description="Environment")
    debug: bool = Field(default=True, description="Debug mode")
    secret_key: str = Field(..., description="Secret key for sessions")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    cors_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="CORS allowed origins"
    )
    
    # Database
    database_url: str = Field(..., description="Database connection URL")
    database_pool_size: int = Field(default=20, description="Connection pool size")
    database_max_overflow: int = Field(default=10, description="Max overflow connections")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    
    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2",
        description="Celery result backend"
    )
    
    # LLM API Keys
    anthropic_api_key: str = Field(..., description="Anthropic API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    
    # LLM Configuration
    anthropic_model_synthesizer: str = Field(
        default="claude-opus-4.1",
        description="Claude model for synthesizer"
    )
    anthropic_model_specialist: str = Field(
        default="claude-sonnet-4.5",
        description="Claude model for specialists"
    )
    max_tokens_specialist: int = Field(
        default=2000,
        description="Max tokens for specialist agents"
    )
    max_tokens_synthesizer: int = Field(
        default=4000,
        description="Max tokens for synthesizer"
    )
    llm_temperature: float = Field(default=0.7, description="LLM temperature")
    llm_timeout: int = Field(default=60, description="LLM timeout in seconds")
    
    # Token Limits & Cost Controls
    max_tokens_per_session: int = Field(
        default=30000,
        description="Maximum tokens per analysis session"
    )
    monthly_token_budget: int = Field(
        default=10000000,
        description="Monthly token budget"
    )
    alert_token_threshold: int = Field(
        default=25000,
        description="Alert when session exceeds this threshold"
    )
    
    # ChromaDB
    chroma_host: str = Field(default="localhost", description="ChromaDB host")
    chroma_port: int = Field(default=8001, description="ChromaDB port")
    chroma_persist_directory: str = Field(
        default="./chroma_data",
        description="ChromaDB persistence directory"
    )
    
    # Qatar Open Data
    qatar_data_dir: str = Field(
        default="../qatar_data",
        description="Qatar Open Data directory"
    )
    qatar_data_update_schedule: str = Field(
        default="0 2 * * 0",
        description="Cron schedule for Qatar data updates (Weekly Sunday 2 AM)"
    )
    
    # PDF Generation
    pdf_output_dir: str = Field(
        default="./output/pdfs",
        description="PDF output directory"
    )
    pdf_template_dir: str = Field(
        default="./app/templates",
        description="PDF template directory"
    )
    
    # Session Configuration
    session_timeout_minutes: int = Field(
        default=120,
        description="Session timeout in minutes"
    )
    max_concurrent_sessions: int = Field(
        default=10,
        description="Maximum concurrent sessions"
    )
    
    # Monitoring & Logging
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")
    posthog_api_key: Optional[str] = Field(default=None, description="PostHog API key")
    posthog_host: str = Field(
        default="https://app.posthog.com",
        description="PostHog host"
    )
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Azure Configuration
    azure_storage_connection_string: Optional[str] = Field(
        default=None,
        description="Azure storage connection string"
    )
    azure_storage_container_name: str = Field(
        default="udc-polaris-pdfs",
        description="Azure storage container"
    )
    
    # Security
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed hosts"
    )
    enable_https_redirect: bool = Field(
        default=False,
        description="Enable HTTPS redirect"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="CORS allow credentials"
    )
    
    # Feature Flags
    enable_caching: bool = Field(default=True, description="Enable caching")
    enable_websockets: bool = Field(default=True, description="Enable WebSockets")
    enable_metrics: bool = Field(default=True, description="Enable metrics")
    enable_rate_limiting: bool = Field(default=True, description="Enable rate limiting")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60,
        description="Rate limit per minute"
    )
    rate_limit_per_hour: int = Field(
        default=1000,
        description="Rate limit per hour"
    )
    
    # Development
    reload: bool = Field(default=True, description="Auto-reload on file changes")
    workers: int = Field(default=1, description="Number of workers")
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from comma-separated string or list."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.env.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.env.lower() == "development"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8", 
        "case_sensitive": False
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Settings: Application settings instance.
        
    Note:
        Settings are cached to avoid repeated environment variable parsing.
    """
    return Settings()


# Convenience export
settings = get_settings()


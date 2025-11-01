"""
UDC Polaris Multi-Agent Strategic Intelligence System - Main Application.

FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

# Import routers
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    
    Handles startup and shutdown tasks.
    
    Args:
        app: FastAPI application instance.
        
    Yields:
        None: Application runs between startup and shutdown.
    """
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📍 Environment: {settings.env}")
    print(f"🔧 Debug mode: {settings.debug}")
    
    # Initialize database connections
    # await init_db()
    
    # Initialize ChromaDB
    # await init_chroma()
    
    # Initialize Redis
    # await init_redis()
    
    # Load Qatar Open Data catalog
    # await load_qatar_data_catalog()
    
    print("✅ Application startup complete")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application...")
    
    # Close database connections
    # await close_db()
    
    # Close Redis connections
    # await close_redis()
    
    print("✅ Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Multi-Agent Strategic Intelligence System for UDC",
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routers
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """
    Root endpoint - API health check.
    
    Returns:
        dict: API status and information.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "environment": settings.env,
        "docs": "/docs" if not settings.is_production else "disabled",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: Health status of application components.
    """
    health_status = {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.env,
        "components": {
            "api": "healthy",
            # "database": await check_db_health(),
            # "redis": await check_redis_health(),
            # "chroma": await check_chroma_health(),
        }
    }
    
    return JSONResponse(content=health_status, status_code=200)


@app.get(f"{settings.api_prefix}/info")
async def api_info():
    """
    API information endpoint.
    
    Returns:
        dict: API capabilities and configuration.
    """
    return {
        "api_version": "v1",
        "features": {
            "agents": 7,
            "debate_rounds": 2,
            "max_analysis_time_minutes": 20,
            "supported_llms": ["anthropic-claude", "openai-gpt4"],
            "output_formats": ["json", "pdf"],
        },
        "agents": {
            "orchestrator": "Dr. Omar Al-Thani",
            "cfo": "Dr. James Chen",
            "market": "Dr. Noor Al-Mansouri",
            "energy": "Dr. Khalid Al-Attiyah",
            "regulatory": "Dr. Fatima Al-Sulaiti",
            "sustainability": "Dr. Marcus Weber",
            "contrarian": "Dr. Sarah Mitchell",
            "synthesizer": "Dr. Hassan Al-Kuwari",
        },
        "data_sources": {
            "qatar_open_data": True,
            "udc_reports": True,
            "ceo_context": True,
        },
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.reload,
        workers=settings.workers,
        log_level=settings.log_level.lower(),
    )


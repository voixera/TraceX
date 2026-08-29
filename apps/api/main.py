"""TraceX API main application."""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging

from packages.common.settings import settings
from packages.common.logging import setup_logging
from packages.database.session import (
    init_database,
    create_tables,
    close_database,
)
from packages.database.models import Base

# Import routers
from apps.api.routers import cases, targets, investigations, entities


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging(debug=settings.debug)
    logger = logging.getLogger(__name__)
    logger.info("Starting TraceX API")

    # Initialize database
    init_database(settings.database_url)
    await create_tables()

    yield

    # Shutdown
    logger.info("Shutting down TraceX API")
    await close_database()


# Create FastAPI app
app = FastAPI(
    title="TraceX API",
    description="Open-Source OSINT Intelligence Platform API",
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cases.router)
app.include_router(targets.router)
app.include_router(investigations.router)
app.include_router(entities.router)

# Security
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Get current user from token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return "anonymous"


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "tracex-api", "version": settings.version}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TraceX API",
        "version": settings.version,
        "docs": "/docs",
        "health": "/health",
    }
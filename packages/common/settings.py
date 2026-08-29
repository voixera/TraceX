"""TraceX settings module."""

import os
from pathlib import Path


class Settings:
    """TraceX application settings."""

    def __init__(self):
        self.debug = os.getenv("TRACEX_DEBUG", "false").lower() == "true"
        self.environment = os.getenv("TRACEX_ENV", "development")
        self.database_url = os.getenv(
            "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/tracex"
        )
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.secret_key = os.getenv("TRACEX_SECRET_KEY", "change-me-in-production")
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.web_host = os.getenv("WEB_HOST", "0.0.0.0")
        self.web_port = int(os.getenv("WEB_PORT", "3000"))
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.bot_admin_ids = [
            int(id.strip())
            for id in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",")
            if id.strip()
        ]

        # Rate limits
        self.rate_limits = {
            "github": {"requests_per_minute": 30},
            "dns": {"requests_per_second": 5},
            "default": {"requests_per_minute": 60},
        }

        # Collector timeouts
        self.collector_timeout = int(os.getenv("COLLECTOR_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("RETRY_DELAY", "1.0"))

        # File paths
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)

        # API configuration
        self.api_v1_prefix = "/api/v1"
        self.project_name = "TraceX"
        self.version = "0.1.0"
        self.description = "Open-Source OSINT Intelligence Platform"


settings = Settings()

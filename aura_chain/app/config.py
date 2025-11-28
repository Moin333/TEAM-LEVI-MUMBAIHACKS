from pydantic_settings import BaseSettings, SettingsConfigDict # Updated import for V2 compatibility
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AURA Chain"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # API Keys
    ANTHROPIC_API_KEY: str
    GOOGLE_API_KEY: str
    OPENAI_API_KEY: str
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/msme_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL: int = 3600  # 1 hour
    
    # Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Agent Configuration
    ORCHESTRATOR_MODEL: str = "claude-sonnet-4-5-20250929"
    DATA_HARVESTER_MODEL: str = "gemini-1.5-flash"
    VISUALIZER_MODEL: str = "claude-sonnet-4-20250514"
    TREND_ANALYST_MODEL: str = "gemini-2.0-flash-exp"
    FORECASTER_MODEL: str = "claude-sonnet-4-20250514"
    MCTS_OPTIMIZER_MODEL: str = "claude-sonnet-4-20250514"
    ORDER_MANAGER_MODEL: str = "gpt-4o"
    NOTIFIER_MODEL: str = "gpt-4o-mini"
    
    # Timeouts & Limits
    API_TIMEOUT: int = 60
    MAX_TOKENS: int = 4000
    MAX_AGENTS_PARALLEL: int = 3
    
    # Observability
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Discord Integration (THIS WAS MISSING)
    DISCORD_WEBHOOK_URL: Optional[str] = None
    
    # Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore" # Changed to 'ignore' so it won't crash on other random env vars
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
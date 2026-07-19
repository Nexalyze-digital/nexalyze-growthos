from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Nexalyze GrowthOS API"
    version: str = "0.1.0"
    ai_provider: str = "mock"
    ai_fallback_provider: str = "mock"
    database_url: str = "sqlite:///data/growthos.db"
    jwt_secret_key: str = "local-development-secret-change-me"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    auth_rate_limit_per_minute: int = 10
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:latest"
    ollama_timeout_seconds: float = 90
    brand_store_path: str = "data/brand-brain.json"
    brand_context_max_characters: int = 4000
    research_store_path: str = "data/research-runs.json"
    research_context_max_characters: int = 4000
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )


settings = Settings()

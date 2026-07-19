from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Nexalyze GrowthOS API"
    version: str = "0.1.0"
    app_env: str = "local"
    ai_provider: str = "mock"
    ai_fallback_provider: str = "mock"
    database_url: str = "sqlite:///data/growthos.db"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_pre_ping: bool = True
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

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        production_envs = {"production", "prod"}
        default_secret = "local-development-secret-change-me"
        if self.app_env.lower() in production_envs and (
            self.jwt_secret_key == default_secret or len(self.jwt_secret_key) < 32
        ):
            raise ValueError("JWT_SECRET_KEY must be set to a strong production secret.")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )


settings = Settings()

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Nexalyze GrowthOS API"
    version: str = "0.1.0"
    provider_name: str = "mock"
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    model_config = SettingsConfigDict(env_file=".env", env_prefix="GROWTHOS_")


settings = Settings()

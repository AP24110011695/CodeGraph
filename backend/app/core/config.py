import os
from pydantic_settings import BaseSettings
from pydantic import Field, model_validator


class Settings(BaseSettings):
    APP_NAME: str = Field(default="CodeGraph", description="Application name")
    APP_VERSION: str = Field(default="1.0.0-rc.1", description="Application version")
    HOST: str = Field(default="127.0.0.1", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    # Storage paths
    UPLOAD_DIR: str = Field(default="uploads", description="Upload directory path")
    STORAGE_DIR: str = Field(default="storage", description="Storage directory path")
    CODEGRAPH_DB_PATH: str | None = Field(default=None, description="SQLite database path (default: storage/codegraph.db)")
    VECTOR_STORAGE_PATH: str | None = Field(default=None, description="Vector storage path (default: storage/vectors)")

    # Optional LLM provider keys (unused unless corresponding provider selected)
    OPENAI_API_KEY: str | None = Field(default=None, description="OpenAI API key")
    ANTHROPIC_API_KEY: str | None = Field(default=None, description="Anthropic API key")
    GEMINI_API_KEY: str | None = Field(default=None, description="Google Gemini API key")
    GROQ_API_KEY: str | None = Field(default=None, description="Groq API key")

    # Safety defaults for RC-1
    EXPOSE_ERROR_DETAILS: bool = Field(
        default=True,
        description="When true, HTTP 500 responses may include exception text (dev only)",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

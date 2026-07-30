from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    APP_NAME: str = Field(default="CodeGraph", description="Application name")
    APP_VERSION: str = Field(default="1.0.0-rc.1", description="Application version")
    APP_ENV: str = Field(default="development", description="Environment")
    HOST: str = Field(default="127.0.0.1", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    # Optional LLM provider keys (unused unless corresponding provider selected)
    OPENAI_API_KEY: str | None = Field(default=None, description="OpenAI API key")
    ANTHROPIC_API_KEY: str | None = Field(default=None, description="Anthropic API key")
    GEMINI_API_KEY: str | None = Field(default=None, description="Google Gemini API key")

    # Safety defaults for RC-1
    EXPOSE_ERROR_DETAILS: bool = Field(
        default=False,
        description="When true, HTTP 500 responses may include exception text (dev only)",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    APP_NAME: str = Field(default="CodeGraph", description="Application name")
    APP_ENV: str = Field(default="development", description="Environment")
    HOST: str = Field(default="127.0.0.1", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

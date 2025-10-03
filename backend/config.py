"""
Configuration management for LLM Safety Playground
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = "LLM Safety Playground"
    version: str = "1.0.0"
    environment: str = "development"

    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Logging
    log_level: str = "INFO"

    # Safety Pipeline
    enable_input_filters: bool = True
    enable_output_filters: bool = True
    block_threshold: float = 0.7
    warning_threshold: float = 0.5

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Timeouts
    llm_timeout: int = 30  # seconds
    max_prompt_length: int = 4000
    max_response_length: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment.lower() == "development"


# Global settings instance
settings = Settings()

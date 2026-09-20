import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    APP_NAME: str = "VaaniCart AI"
    APP_TAGLINE: str = "Your AI Shopping Assistant — Just Ask."
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    DEBUG: bool = True

    # LLM Settings
    LLM_PROVIDER: str = "gemini"  # "gemini" | "openai" | "local"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Prompt versions
    PROMPT_VERSION_INTENT: str = "v1"
    PROMPT_VERSION_VOICE: str = "v1"
    PROMPT_VERSION_RAG: str = "v1"

    # RAG Settings
    RAG_TOP_K: int = 4

    # Catalog Provider
    PRODUCT_PROVIDER: str = "mock"  # "mock" | "shopify"
    SHOPIFY_STORE_DOMAIN: str = ""
    SHOPIFY_STOREFRONT_ACCESS_TOKEN: str = ""

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            import json
            try:
                return json.loads(v)
            except Exception:
                return ["*"]
        return v

settings = Settings()

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    # App Config
    APP_NAME: str = "AgriVLA"
    ENVIRONMENT: str = "development"
    
    # Model Config
    MODEL_PROVIDER: str = "gemini"
    MODEL_NAME: str = "gemini-3.6-flash"
    GEMINI_API_KEY: str = ""

    # RAG Config
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_STORE_URL: str = "./data/knowledge/qdrant"

    # Database Config
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "agrivla"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Agent Config
    MAX_AGENT_STEPS: int = 10
    HIGH_CONFIDENCE_THRESHOLD: float = 0.75
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.50
    RANDOM_SEED: int = 42

    # Authentication
    JWT_SECRET_KEY: str = "change_me_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

# Removed HF_TOKEN logic since we are using Gemini API now

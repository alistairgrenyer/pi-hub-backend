import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pi-Hub Backend"
    API_V1_STR: str = "/api"
    
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    DATABASE_URL: str

    # Paths
    INBOX_DIR: str = "/data/inbox"
    VAULT_DIR: str = "/data/vault"
    MODEL_DIR: str = "/models"

    # Models
    WHISPER_MODEL_SIZE: str = "base"
    LLM_MODEL_PATH: str = "/models/llama-2-7b-chat.Q4_K_M.gguf" # Example default

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()

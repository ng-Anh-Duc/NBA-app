"""Application settings and configuration."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SalesforceSettings(BaseSettings):
    """Salesforce configuration settings."""
    username: str = os.getenv("SALESFORCE_USERNAME", "")
    password: str = os.getenv("SALESFORCE_PASSWORD", "")
    security_token: str = os.getenv("SALESFORCE_SECURITY_TOKEN", "")
    domain: str = os.getenv("SALESFORCE_DOMAIN", "login")
    
    class Config:
        env_prefix = "SALESFORCE_"

class LLMSettings(BaseSettings):
    """LLM configuration settings."""
    provider: str = os.getenv("LLM_PROVIDER", "openai")
    model: str = os.getenv("LLM_MODEL", "gpt-4")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    class Config:
        env_prefix = "LLM_"

class AppSettings(BaseSettings):
    """Application settings."""
    env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    streamlit_port: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    data_dir: Path = base_dir / "data"
    logs_dir: Path = base_dir / "logs"
    
    class Config:
        env_prefix = "APP_"

# Instantiate settings
salesforce_settings = SalesforceSettings()
llm_settings = LLMSettings()
app_settings = AppSettings()

# Create directories
app_settings.data_dir.mkdir(exist_ok=True)
app_settings.logs_dir.mkdir(exist_ok=True)
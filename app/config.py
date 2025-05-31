from pydantic_settings import BaseSettings
from typing import Optional
from typing import List

class Settings(BaseSettings):
    # Database
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Email Configuration
    GMAIL_USER: str
    GMAIL_CLIENT_ID: str
    GMAIL_CLIENT_SECRET: str
    GMAIL_REFRESH_TOKEN: str

    # Groq API Configuration
    GROQ_API_KEY: str

    # Server Configuration
    PORT: int = 8000
    ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS Configuration
    CORS_ORIGINS: str = '["http://localhost:3000"]'
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 
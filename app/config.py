from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Email (simplified for now)
    GMAIL_USER: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 
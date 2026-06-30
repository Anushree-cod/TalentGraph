import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TalentGraph"
    API_V1_STR: str = "/api"
    # Secret key for JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    # Database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./talentgraph.db")

settings = Settings()

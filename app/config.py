from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

if os.getenv("ENV") != "production":
    load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    db_user: str
    db_password: str
    db_name: str
    db_host: str

    # Non-sensitive default settings
    # LLM Model Details
    MODEL: str
    temperature: float=0
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

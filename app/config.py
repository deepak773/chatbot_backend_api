from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

if os.getenv("ENV") != "production":
    load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    SERVICE_ACCOUNT_FILE: str
    db_user: str
    db_password: str
    db_name: str
    db_host: str

    # Non-sensitive default settings
    # LLM Model Details
    MODEL: str="gpt-4o"
    temperature: float=0.1
    prompt: str = """
    You are an expert SQL assistant. Your task is to understand the user's natural language query, generate the corresponding SQL query, and retrieve the data from the database.

    If the retrieved data is in a tabular format, present it clearly as a table with appropriate headings. If the data does not require tabular representation, respond in a clear and concise natural language format.

    User query: {query}

    Provide your response below.
    """
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

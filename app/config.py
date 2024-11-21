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

    FOLDER_ID: str = "1c5hzYr0gDtm4AZlrDsVYMaXOg9YLRPxH"
    SHEET_ID: str ="1qHJryc75YqA9U8V8y85iuZbxuSgUiRtIqFSPHFVrlRM"
    ALL_WORKSHEETS: list =['AC Dashboard',
        'PC Dashboard',
        'AC Mapping',
        'New Administrative Divisions',
        'MLA Details',
        'LS MP Details',
        'RS MP Details',
        'Zila Pramukh-Up Pramukh',
        'District Presidents',
        'By Poll Details',
        'Former BJP MLA Candidates',
        'Former INC MLA Candidates',
        'Former BJP MP Candidates',
        'Former INC MP Candidates',
        'Zila Parishad Members',
        '2023 Cabinets',
        '2018-23 Cabinet',
        '2013-18 Cabinets',
        'Mandal Mapping_July 24',
        'Document Repository',
        'Booth Mapping_July 24',
        'Past Elections Backend',
        '2023 Results',
        'PC Level Results',
        'Pre 2023 ECI Results',
        'Backend',
        '2024 AC Results']
    ELIGIBLE_WORKSHEETS: list =["AC Mapping"]
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

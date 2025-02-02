from fastapi import APIRouter, HTTPException
from app.config import settings
import app.utils.genai as genai
from app.utils.crew_ai_tool import process_user_request

# Create a router instance
router = APIRouter()

@router.post("/generate")
async def generate_response(query: str):
    try:
        #DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}/{settings.db_name}?sslmode=require"
        #engine = genai.create_sql_engine(DATABASE_URL)
        #llm = genai.get_chat_model(settings.MODEL, settings.OPENAI_API_KEY, settings.temperature)
        #sql_agent = genai.get_sql_agent(engine, settings.prompt, llm)
        #response = genai.get_response_from_agent(sql_agent, query)
        #return response
        result = process_user_request(query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

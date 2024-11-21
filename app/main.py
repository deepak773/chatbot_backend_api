from fastapi import FastAPI
from app.config import settings
from app.routes import router as api_router
from vercel import Vercel

# Create FastAPI app
app = FastAPI(
    title="OpenAI FastAPI Integration",
    description="A FastAPI app using OpenAI's models via LangChain",
    version="1.0.0"
)

# Include routes
app.include_router(api_router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the OpenAI-powered FastAPI application!"}

app = Vercel(app)
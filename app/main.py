from fastapi import FastAPI
from app.routes import router as api_router
import uvicorn

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

if __name__ == "__main__":
    # Read the port from the environment variable or use the default (8080)
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
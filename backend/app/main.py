import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.db import init_db
from app.services.parser import ErrorParser

# Load environment variables
load_dotenv()

# Configure logging for the entire application
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="DebugAI API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Run this function exactly once, when the application first starts up
@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
async def root():

    return {"message": "Welcome to DebugAI API with Supabase"}


@app.get("/api/test")
async def test_endpoint(error_logs: str):
    parser = ErrorParser()
    parsed_data = parser.parse(error_logs)
    return {"parsed_data": parsed_data}

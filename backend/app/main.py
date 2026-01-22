import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.api import api_router

# Load environment variables
load_dotenv()

# Configure logging for the entire application
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="DebugAI API", version="1.0.0")

# Get allowed origins from environment variable (comma-separated)
# Default includes localhost for development
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_str.split(",")]

# Log CORS configuration for debugging
logging.info(f"CORS allowed origins: {ALLOWED_ORIGINS}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


# Run this function exactly once, when the application first starts up
@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
async def root():
    return {"message": "Welcome to DebugAI API with Supabase"}


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return {"status": "healthy", "service": "DebugAI API"}

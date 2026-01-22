from fastapi import APIRouter

from app.api.analyze import router as analyze_router
from app.api.scrape_routes import router as scrape_router
from app.api.embeddings_routes import router as embeddings_router
from app.api.feedback import router as feedback_router
from app.api.analytics import router as analytics_router

api_router = APIRouter(prefix="/api")

api_router.include_router(analyze_router)
api_router.include_router(scrape_router)
api_router.include_router(embeddings_router)
api_router.include_router(feedback_router)
api_router.include_router(analytics_router)

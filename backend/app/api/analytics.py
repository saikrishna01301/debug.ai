from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.db.crud import (
    get_total_analyses,
    get_total_errors,
    get_errors_by_language,
    get_avg_analysis_time,
    get_total_feedback,
    get_successful_feedback,
    get_language_breakdown,
)
from app.services.cache import CacheService
from app.services.cost_tracker import get_total_cost, get_daily_costs, get_cost_breakdown

router = APIRouter()
cache = CacheService()


@router.get("/analytics/overview")
async def get_analytics_overview(session: AsyncSession = Depends(get_session)):
    """
    Get overall system analytics
    """
    total_analyses = await get_total_analyses(session)
    total_errors = await get_total_errors(session)
    errors_by_language = await get_errors_by_language(session)
    avg_analysis_time = await get_avg_analysis_time(session)
    total_feedback = await get_total_feedback(session)
    successful_feedback = await get_successful_feedback(session)

    return {
        "total_analyses": total_analyses,
        "total_errors_parsed": total_errors,
        "avg_analysis_time_ms": int(avg_analysis_time),
        "errors_by_language": [
            {"language": lang or "unknown", "count": count}
            for lang, count in errors_by_language
        ],
        "feedback": {
            "total": total_feedback,
            "successful": successful_feedback,
            "success_rate": (
                successful_feedback / total_feedback if total_feedback > 0 else 0
            ),
        },
    }


@router.get("/analytics/language-breakdown")
async def get_language_breakdown_endpoint(session: AsyncSession = Depends(get_session)):
    """
    Get detailed breakdown by programming language
    """
    breakdown = await get_language_breakdown(session)

    return [
        {
            "language": lang or "unknown",
            "total_errors": total,
            "avg_confidence": round(avg_conf or 0, 1),
        }
        for lang, total, avg_conf in breakdown
    ]


@router.get("/analytics/cache-stats")
async def get_cache_stats():
    """
    Get cache statistics
    """
    return cache.get_stats()


@router.get("/analytics/costs")
async def get_costs_overview(
    days: int = 30, session: AsyncSession = Depends(get_session)
):
    """
    Get cost analytics overview
    """
    total = await get_total_cost(session, days)
    breakdown = await get_cost_breakdown(session, days)
    daily = await get_daily_costs(session, min(days, 7))

    return {
        "total_cost": total,
        "breakdown": breakdown,
        "daily": daily,
    }

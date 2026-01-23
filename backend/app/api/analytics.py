from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.db import get_session, Feedback
from app.db.models import ParsedError, Analysis

from app.services.cache import CacheService

router = APIRouter()
cache = CacheService()


@router.get("/analytics/overview")
async def get_analytics_overview(session: AsyncSession = Depends(get_session)):
    """
    Get overall system analytics
    """
    # Total analyses
    total_analyses_result = await session.execute(select(func.count(Analysis.id)))
    total_analyses = total_analyses_result.scalar()

    # Total errors parsed
    total_errors_result = await session.execute(select(func.count(ParsedError.id)))
    total_errors = total_errors_result.scalar()

    # Errors by language
    errors_by_language_query = select(
        ParsedError.language, func.count(ParsedError.id).label("count")
    ).group_by(ParsedError.language)
    errors_by_language_result = await session.execute(errors_by_language_query)
    errors_by_language = errors_by_language_result.all()

    # Average analysis time
    avg_time_result = await session.execute(select(func.avg(Analysis.analysis_time)))
    avg_analysis_time = avg_time_result.scalar() or 0

    # Feedback stats
    total_feedback_result = await session.execute(select(func.count(Feedback.id)))
    total_feedback = total_feedback_result.scalar()

    successful_feedback_result = await session.execute(
        select(func.count(Feedback.id)).where(Feedback.worked == True)
    )
    successful_feedback = successful_feedback_result.scalar()

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
async def get_language_breakdown(session: AsyncSession = Depends(get_session)):
    """
    Get detailed breakdown by programming language
    """
    breakdown_query = select(
        ParsedError.language,
        func.count(ParsedError.id).label("total_errors"),
        func.avg(ParsedError.confidence_score).label("avg_confidence"),
    ).group_by(ParsedError.language)

    breakdown_result = await session.execute(breakdown_query)
    breakdown = breakdown_result.all()

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

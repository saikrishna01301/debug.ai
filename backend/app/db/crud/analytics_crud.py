from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.db import Feedback
from app.db.models import ParsedError, Analysis


async def get_total_analyses(session: AsyncSession) -> int:
    """Get total number of analyses"""
    result = await session.execute(select(func.count(Analysis.id)))
    return result.scalar() or 0


async def get_total_errors(session: AsyncSession) -> int:
    """Get total number of parsed errors"""
    result = await session.execute(select(func.count(ParsedError.id)))
    return result.scalar() or 0


async def get_errors_by_language(session: AsyncSession) -> list:
    """Get error count grouped by programming language"""
    query = select(
        ParsedError.language, func.count(ParsedError.id).label("count")
    ).group_by(ParsedError.language)
    result = await session.execute(query)
    return result.all()


async def get_avg_analysis_time(session: AsyncSession) -> float:
    """Get average analysis time in milliseconds"""
    result = await session.execute(select(func.avg(Analysis.analysis_time)))
    return result.scalar() or 0


async def get_total_feedback(session: AsyncSession) -> int:
    """Get total number of feedback entries"""
    result = await session.execute(select(func.count(Feedback.id)))
    return result.scalar() or 0


async def get_successful_feedback(session: AsyncSession) -> int:
    """Get number of successful feedback entries"""
    result = await session.execute(
        select(func.count(Feedback.id)).where(Feedback.worked == True)
    )
    return result.scalar() or 0


async def get_language_breakdown(session: AsyncSession) -> list:
    """Get detailed breakdown by programming language with confidence scores"""
    query = select(
        ParsedError.language,
        func.count(ParsedError.id).label("total_errors"),
        func.avg(ParsedError.confidence_score).label("avg_confidence"),
    ).group_by(ParsedError.language)
    result = await session.execute(query)
    return result.all()

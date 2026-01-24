from datetime import datetime, timedelta
from app.db import CostTracking
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, cast, Date


async def create_cost_record(
    session: AsyncSession,
    operation: str,
    model: str,
    cost: float,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
) -> CostTracking:
    record = CostTracking(
        operation=operation,
        model=model,
        cost=cost,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


# Get total cost for last N days
async def total_cost(session: AsyncSession, days: int = 30):
    since = datetime.utcnow() - timedelta(days=days)
    result = await session.execute(
        select(func.sum(CostTracking.cost)).filter(CostTracking.created_at >= since)
    )
    total = result.scalar()
    return total or 0.0


async def cost_breakdown(session: AsyncSession, days: int = 30) -> list:
    """
    Get cost breakdown by operation
    """
    since = datetime.utcnow() - timedelta(days=days)

    result = await session.execute(
        select(
            CostTracking.operation,
            func.count(CostTracking.id).label("count"),
            func.sum(CostTracking.cost).label("total_cost"),
            func.sum(CostTracking.total_tokens).label("total_tokens"),
        )
        .filter(CostTracking.created_at >= since)
        .group_by(CostTracking.operation)
    )
    breakdown = result.all()

    return [
        {
            "operation": op,
            "count": count,
            "total_cost": float(total_cost or 0),
            "total_tokens": int(total_tokens or 0),
        }
        for op, count, total_cost, total_tokens in breakdown
    ]


async def daily_costs(session: AsyncSession, days: int = 7) -> list:
    """
    Get daily cost summary
    """
    since = datetime.utcnow() - timedelta(days=days)

    result = await session.execute(
        select(
            cast(CostTracking.created_at, Date).label("date"),
            func.sum(CostTracking.cost).label("cost"),
        )
        .filter(CostTracking.created_at >= since)
        .group_by(cast(CostTracking.created_at, Date))
        .order_by(cast(CostTracking.created_at, Date))
    )
    daily = result.all()

    return [
        {"date": date.isoformat(), "cost": float(cost or 0)} for date, cost in daily
    ]

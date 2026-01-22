from app.db import get_session, Feedback
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, Integer, select
from app.db.crud import create_feedback

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackRequest, session: AsyncSession = Depends(get_session)
):
    result = await create_feedback(feedback, session)
    return result


@router.get("/analytics/feedback-stats")
async def get_feedback_stats(session: AsyncSession = Depends(get_session)):
    """
    Get overall feedback statistics
    """
    # Total feedback
    total_result = await session.execute(select(func.count(Feedback.id)))
    total = total_result.scalar()

    # Successful solutions
    successful_result = await session.execute(
        select(func.count(Feedback.id)).where(Feedback.worked == True)
    )
    successful = successful_result.scalar()

    # Success rate by solution index
    solution_stats_query = select(
        Feedback.solution_index,
        func.count(Feedback.id).label('total'),
        func.sum(func.cast(Feedback.worked, Integer)).label('successful')
    ).group_by(Feedback.solution_index)

    solution_stats_result = await session.execute(solution_stats_query)
    solution_stats = solution_stats_result.all()

    solution_breakdown = []
    for idx, total_count, success_count in solution_stats:
        solution_breakdown.append({
            'solution_index': idx,
            'total_feedback': total_count,
            'successful': success_count or 0,
            'success_rate': (success_count or 0) / total_count if total_count > 0 else 0
        })

    return {
        'total_feedback': total,
        'total_successful': successful,
        'overall_success_rate': successful / total if total > 0 else 0,
        'solution_breakdown': solution_breakdown
    }

from app.db import Base, Feedback
from sqlalchemy.ext.asyncio import AsyncSession


async def create_feedback(feedback_request, session):
    feedback = Feedback(**feedback_request.model_dump())
    session.add(feedback)
    await session.commit()
    await session.refresh(feedback)
    return feedback

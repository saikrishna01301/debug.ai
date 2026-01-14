from app.db import StackOverFlowPost, get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists


async def post_exists(session: AsyncSession, question_id: int) -> bool:
    """Check if a Stack Overflow post already exists in the database"""
    stmt = select(exists().where(StackOverFlowPost.question_id == question_id))
    result = await session.execute(stmt)
    return result.scalar()


async def create_post(session: AsyncSession, post_data: dict) -> StackOverFlowPost:
    """Create a new Stack Overflow post in the database"""
    post = StackOverFlowPost(**post_data)
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post

async def get_all_posts(session: AsyncSession):
    """Get all Stack Overflow posts from the database"""
    stmt = select(StackOverFlowPost)
    result = await session.execute(stmt)
    return result.scalars().all() 
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core import config
from app.db import Base

DB_URL = config.DATABASE_URL
engine = create_async_engine(DB_URL, echo=True)

sessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Dependency (to be used in routes for getting DB session)
async def get_session() -> AsyncSession:
    async with sessionLocal() as session:
        yield session


# need to shift to main.py later
# create tables on startup if not exist
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

from typing import Annotated
from .config import env
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

async_engine = create_async_engine(
    env.SQLALCHEMY_DATABASE_URL
)

AsyncSessionMaker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    future=True
)


# Async Dependency
async def get_db() -> AsyncSession:
    async with AsyncSessionMaker() as session:
        yield session


GetDb = Annotated[AsyncSession, Depends(get_db)]

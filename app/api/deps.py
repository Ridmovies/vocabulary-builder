from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


DBSession: type[AsyncSession] = Annotated[AsyncSession, Depends(get_db)]
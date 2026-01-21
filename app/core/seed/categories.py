from sqlalchemy import select
from app.models import Category
from app.core.database import AsyncSessionLocal

CATEGORIES = [
    {"name": "Basic", "description": "Самые простые слова"},
    {"name": "default", "description": "По умолчанию"},
]

async def seed_categories():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for c in CATEGORIES:
                result = await session.execute(
                    select(Category).where(Category.name == c["name"], Category.owner_id == None)
                )
                if result.scalar_one_or_none():
                    continue

                session.add(Category(**c))

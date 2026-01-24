import asyncio

from app.core.database import AsyncSessionLocal
from app.core.seed.system_seeds import seed_system_categories
from app.core.seed.users import seed_users

async def run_seeds():
    async with AsyncSessionLocal() as session:
        await seed_system_categories(session)
        await seed_users(session)
        await session.commit()
        # можно вызвать сиды для пользователей отдельно



if __name__ == "__main__":
    asyncio.run(run_seeds())

# python -m app.core.seed.run

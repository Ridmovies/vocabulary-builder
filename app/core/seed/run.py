from app.core.database import AsyncSessionLocal
from app.core.seed.system_seeds import seed_system_categories
from app.core.seed.users import seed_users

async def run_seeds():
    async with AsyncSessionLocal() as session:
        await seed_system_categories(session)
        await seed_users(session)
        # можно вызвать сиды для пользователей отдельно



# python -m app.core.seed.run

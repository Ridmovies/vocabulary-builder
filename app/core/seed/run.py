from app.core.database import AsyncSessionLocal
from app.core.seed.system_seeds import seed_system_categories
from app.core.seed.users import seed_users
from app.core.seed.categories import seed_categories
from app.core.seed.words import seed_words

# async def run_seeds():
#     await seed_users()
#     await seed_categories()
#     await seed_words()

async def run_seeds():
    async with AsyncSessionLocal() as session:
        await seed_system_categories(session)
        # можно вызвать сиды для пользователей отдельно



# python -m app.core.seed.run
# psql -U postgres -c "DROP DATABASE IF EXISTS vocabulary WITH (FORCE); CREATE DATABASE vocabulary;"
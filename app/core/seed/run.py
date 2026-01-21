from app.core.seed.users import seed_users
from app.core.seed.categories import seed_categories
from app.core.seed.words import seed_words

async def run_seeds():
    await seed_users()
    await seed_categories()
    await seed_words()



# python -m app.core.seed.run
# psql -U postgres -c "DROP DATABASE IF EXISTS vocabulary WITH (FORCE); CREATE DATABASE vocabulary;"
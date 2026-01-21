from sqlalchemy import select
from app.models import User
from app.core.database import AsyncSessionLocal
from app.utils.pwd import get_password_hash

USERS = [
    {"email": "user@example.com", "username": "user", "password": "string"},
]

async def seed_users():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Получаем всех существующих пользователей
            existing_users = await session.execute(select(User))
            existing_users = {u.email: u for u in existing_users.scalars().all()}

            for u in USERS:
                if u["email"] not in existing_users:
                    hashed_password = get_password_hash(u["password"])
                    user_obj = User(
                        email=u["email"],
                        username=u["username"],
                        hashed_password=hashed_password,
                        is_superuser=False,
                        is_active=True,
                        is_verified=True,  # можно выставить True для сида
                    )
                    session.add(user_obj)

        await session.commit()
    print("User seed completed!")
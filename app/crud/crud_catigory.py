from fastapi import HTTPException
from sqlalchemy import select, or_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    """
    CRUD operations for Category model
    """

    async def get_multi_for_user(
            self,
            db: AsyncSession,
            *,
            user_id: int,
            scope: str = "all",
            skip: int = 0,
            limit: int = 100,
    ) -> list[Category]:
        """
        Получить категории:
        - all    → системные + пользовательские
        - system → только системные
        - mine   → только пользователя
        """

        stmt = select(Category)

        if scope == "system":
            stmt = stmt.where(Category.owner_id.is_(None))

        elif scope == "mine":
            stmt = stmt.where(Category.owner_id == user_id)

        else:  # all
            stmt = stmt.where(
                or_(
                    Category.owner_id.is_(None),
                    Category.owner_id == user_id,
                )
            )

        stmt = stmt.order_by(
            case(
                (Category.owner_id.is_(None), 1),
                else_=0
            ),
            Category.name.asc()
        )

        stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_for_user(
        self,
        db: AsyncSession,
        *,
        obj_in: CategoryCreate,
        owner_id: int,
    ) -> Category:
        category = Category(
            **obj_in.model_dump(),
            owner_id=owner_id,
        )
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category


    async def remove_for_user(
            self,
            db: AsyncSession,
            category_id: int,
            owner_id: int,
    ):
        query = select(self.model).where(Category.id == category_id, Category.owner_id == owner_id)
        result = await db.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            await db.commit()
            return obj
        raise HTTPException(status_code=404, detail="Category not found")


category_crud = CRUDCategory(Category)
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    """
    CRUD operations for Category model
    """

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

category_crud = CRUDCategory(Category)
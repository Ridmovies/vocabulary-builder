from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str
    description: str


class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int

class CategoryUpdate(BaseModel):
    name: str | None = Field(None)
    description: str | None = Field(None)

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class UserLogin(BaseModel):
    """Схема для входа."""
    email: str = Field(
        ...,
        examples=["user@example.com"]
    )
    password: str
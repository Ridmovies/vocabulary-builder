from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class UserLogin(BaseModel):
    """Схема для входа."""
    email: str 
    password: str
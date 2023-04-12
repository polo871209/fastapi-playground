from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# Post
class Post(BaseModel):
    title: str
    content: str
    publish: Optional[bool] = True


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    publish: bool
    created_at: datetime

    class Config:
        orm_mode = True


# User
class UserBase(BaseModel):
    email: EmailStr


class UseCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, conint


# User
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


# Post
class Post(BaseModel):
    id: int
    title: str
    content: str
    publish: bool
    created_at: datetime
    owner: UserOut

    class Config:
        orm_mode = True


class PostCreate(BaseModel):
    title: str
    content: str
    publish: Optional[bool] = True


class PostOut(BaseModel):
    Post: Post
    likes: int


# login
class Login(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str]


# like
class Like(BaseModel):
    post_id: int
    dir: conint(le=1)

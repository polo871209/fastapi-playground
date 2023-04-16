from datetime import datetime
from typing import Optional, List, Any

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


# login
class Login(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str]


# Post
class PostCommentOut(BaseModel):
    user_id: int
    comment: str

    class Config:
        orm_mode = True


class Post(BaseModel):
    id: int
    title: str
    content: str
    publish: bool
    created_at: datetime
    owner: UserOut
    comments: List[PostCommentOut]

    class Config:
        orm_mode = True


class PostCreate(BaseModel):
    title: str
    content: str
    publish: Optional[bool] = True

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    likes: int

    class Config:
        orm_mode = True


# like
class Like(BaseModel):
    post_id: int
    dir: conint(le=1)


# comment
class CommentCreate(BaseModel):
    comment: str


class CommentOut(BaseModel):
    id: int
    comment: str

    class Config:
        orm_mode = True

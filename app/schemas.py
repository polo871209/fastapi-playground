from datetime import datetime
from typing import Optional, List

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


# like
class Like(BaseModel):
    post_id: int
    dir: conint(le=1)


class LikeOut(BaseModel):
    user_id: int

    class Config:
        orm_mode = True


# Post
class PostCommentOut(BaseModel):
    user_id: int
    comment: str

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    publish: bool
    created_at: datetime
    owner: UserOut
    comments: List[PostCommentOut]
    likes: List[LikeOut]

    class Config:
        orm_mode = True


class PostCreate(BaseModel):
    title: str
    content: str
    publish: Optional[bool] = True


# comment
class CommentCreate(BaseModel):
    comment: str


class CommentOut(BaseModel):
    id: int
    comment: str

    class Config:
        orm_mode = True

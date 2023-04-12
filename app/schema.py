from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Post(BaseModel):
    title: str
    content: str
    publish: Optional[bool] = True


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True

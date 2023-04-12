from sqlalchemy import Column, Integer, String, Boolean, text
from sqlalchemy.sql import expression, sqltypes

from .database import Base


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(String(100), nullable=False)
    publish = Column(Boolean, server_default=expression.true(), nullable=False)
    created_at = Column(sqltypes.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

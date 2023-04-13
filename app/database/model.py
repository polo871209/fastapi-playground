from datetime import datetime
from typing import Annotated

from sqlalchemy import text, String
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql import expression
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.database.database import mapper_registry

# unique type
str_100 = Annotated[str, mapped_column(String(100))]
unique_str_100 = Annotated[str_100, mapped_column(unique=True)]
int_primary_key = Annotated[int, mapped_column(primary_key=True)]
create_time = Annotated[datetime, mapped_column(TIMESTAMP(timezone=True), server_default=text('now()'))]


@mapper_registry.mapped
class Post:
    __tablename__ = 'posts'

    id: Mapped[int_primary_key]
    # user_id = Column(Integer, nullable=False)
    title: Mapped[str_100]
    content: Mapped[str_100]
    publish: Mapped[bool] = mapped_column(server_default=expression.true())
    created_at: Mapped[create_time]


@mapper_registry.mapped
class User:
    __tablename__ = 'users'

    id: Mapped[int_primary_key]
    email: Mapped[unique_str_100]
    password: Mapped[str_100]
    created_at: Mapped[create_time]

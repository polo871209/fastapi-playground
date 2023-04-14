from datetime import datetime
from typing import Annotated

from sqlalchemy import text, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import expression
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.database.database import mapper_registry

# unique type
str_100 = Annotated[str, mapped_column(String(100))]
str_100_unique = Annotated[str_100, mapped_column(unique=True)]
int_primary_key = Annotated[int, mapped_column(primary_key=True)]
bool_default_true = Annotated[bool, mapped_column(server_default=expression.true())]
create_time = Annotated[datetime, mapped_column(TIMESTAMP(timezone=True), server_default=text('now()'))]


@mapper_registry.mapped
class User:
    __tablename__ = 'users'

    id: Mapped[int_primary_key]
    email: Mapped[str_100_unique]
    password: Mapped[str_100]
    created_at: Mapped[create_time]


@mapper_registry.mapped
class Post:
    __tablename__ = 'posts'

    id: Mapped[int_primary_key]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='cascade'))
    title: Mapped[str_100]
    content: Mapped[str_100]
    publish: Mapped[bool_default_true]
    created_at: Mapped[create_time]

    owner = relationship('User')

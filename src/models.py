from datetime import datetime
from typing import Annotated, List, Optional

from sqlalchemy import text, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship, registry
from sqlalchemy.sql import expression
from sqlalchemy.sql.sqltypes import TIMESTAMP

mapper_registry = registry()

# unique type
str_100 = Annotated[str, mapped_column(String(100))]
str_100_unique = Annotated[str_100, mapped_column(unique=True)]
int_primary_key = Annotated[int, mapped_column(primary_key=True)]
bool_default_true = Annotated[bool, mapped_column(server_default=expression.true())]
create_time = Annotated[datetime, mapped_column(TIMESTAMP(timezone=True), server_default=text('now()'))]


@mapper_registry.mapped
class DbUser:
    __tablename__ = 'users'

    id: Mapped[int_primary_key]
    email: Mapped[str_100_unique]
    password: Mapped[str_100]
    created_at: Mapped[create_time]

    # posts: Mapped['DbPost'] = relationship(back_populates='owner')
    # comments: Mapped['DbComment'] = relationship(back_populates='owner')


@mapper_registry.mapped
class DbPost:
    __tablename__ = 'posts'

    id: Mapped[int_primary_key]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='cascade'))
    title: Mapped[str_100]
    content: Mapped[str_100]
    publish: Mapped[bool_default_true]
    created_at: Mapped[create_time]

    # owner: Mapped['DbUser'] = relationship(back_populates='posts')
    # likes: Mapped[Optional[List['DbPostLike']]] = relationship()
    # comments: Mapped[Optional[List['DbComment']]] = relationship(back_populates='post')


@mapper_registry.mapped
class DbPostLike:
    __tablename__ = 'posts_likes'

    user_id: Mapped[int_primary_key] = mapped_column(ForeignKey('users.id', ondelete='cascade'))
    post_id: Mapped[int_primary_key] = mapped_column(ForeignKey('posts.id', ondelete='cascade'))
#
#
@mapper_registry.mapped
class DbComment:
    __tablename__ = 'comments'

    id: Mapped[int_primary_key]
    comment: Mapped[str_100]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='cascade'))
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id', ondelete='cascade'))
#
#     owner: Mapped['DbUser'] = relationship(back_populates='comments')
#     post: Mapped['DbPost'] = relationship(back_populates='comments')
#
#
@mapper_registry.mapped
class DbUserFile:
    __tablename__ = 'user_file'

    user_id: Mapped[int_primary_key] = mapped_column(ForeignKey('users.id', ondelete='cascade'))
    file_name: Mapped[str_100] = mapped_column(primary_key=True)
    s3_key_name: Mapped[str_100]

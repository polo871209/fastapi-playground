from typing import Annotated, Optional, Type

import uvicorn
from fastapi import HTTPException, Depends, Body, status, FastAPI, Query, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, insert, update, column, text, delete
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.models import DbPost, DbUser, DbPostLike
from src.oauth2 import create_access_token, UserLogin
from src.schemas import PostCreate, UserOut, UserCreate, Like
from src.utils.hash import verify_password, get_password_hash

async_engine = create_async_engine('mysql+aiomysql://user:password@localhost/fastapi', future=True)
AsyncSessionMaker = async_sessionmaker(async_engine, class_=AsyncSession, future=True)


# Async Dependency
async def get_db() -> AsyncSession:
    async with AsyncSessionMaker() as session:
        yield session


GetDb = Annotated[AsyncSession, Depends(get_db)]

app = FastAPI()


def check_user_exist(user: Type[DbUser]) -> None:
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')


def check_password(plain_password: str, hashed_password: str) -> None:
    if not verify_password(plain_password, hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')


@app.post('/login')
async def login(db: GetDb, payload: OAuth2PasswordRequestForm = Depends()):
    stmt = select(DbUser).where(DbUser.email == payload.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    check_user_exist(user)  # Make sure check_user_exist is async or update accordingly
    check_password(payload.password, user.password)  # Make sure check_password is async or update accordingly

    access_token = create_access_token({'user_id': user.id})
    return {'access_token': access_token, 'token_type': 'bearer'}


# def check_post_exist(post):
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")
#
#
# @app.post('/', status_code=status.HTTP_201_CREATED)
# async def create_post(
#         db: GetDb, user: UserLogin,
#         payload: PostCreate = Body()
# ):
#     new_post_data = payload.dict()
#     new_post_data["user_id"] = user.id
#
#     # Insert the new post
#     stmt = insert(DbPost).values(**new_post_data)
#     await db.execute(stmt)
#     await db.commit()
#
#     # Fetch the newly inserted post
#     stmt = select(DbPost).where(DbPost.user_id == user.id).order_by(DbPost.created_at.desc()).limit(1)
#     result = await db.execute(stmt)
#     new_post = result.scalar_one()
#
#     return new_post
#
#
# @app.get('/all')
# async def get_all_posts(
#         db: GetDb, user: UserLogin,
#         limit: Optional[int] = Query(default=10, description='maximum amount of posts'),
#         search: Optional[str] = Query(default='', description='search in title')
# ):
#     """get all posts"""
#     stmt = select(DbPost).where(DbPost.title.contains(search)).limit(limit)
#     result = await db.execute(stmt)
#     posts = result.scalars().all()
#     return posts
#
#
# @app.get('/{post_id}')
# async def get_post(
#         db: GetDb, user: UserLogin,
#         post_id: int = Path()
# ):
#     """get post by id"""
#     stmt = select(DbPost).where(DbPost.id == post_id)
#     result = await db.execute(stmt)
#     post = result.scalar_one_or_none()
#
#     await check_post_exist(post)
#
#     return post
#
#
# @app.put('/{post_id}', status_code=status.HTTP_202_ACCEPTED)
# async def update_post(
#         db: GetDb, user: UserLogin,
#         post_id: int = Path(),
#         payload: PostCreate = Body()):
#     stmt = (
#         update(DbPost)
#         .where(DbPost.id == post_id, DbPost.user_id == user.id)
#         .values(**payload.dict())
#     )
#     await db.execute(stmt)
#     await db.commit()
#
#     stmt = select(DbPost).where(DbPost.id == post_id)
#     result = await db.execute(stmt)
#     post = result.scalar_one_or_none()
#
#     check_post_exist(post)
#
#     return post
#
#
# @app.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
# async def delete_post(
#         db: GetDb, user: UserLogin,
#         post_id: int = Path()) -> None:
#     """delete post by id"""
#     # Check if post exists and if the user owns the post
#     stmt = select(DbPost).where(DbPost.id == post_id, DbPost.user_id == user.id)
#     result = await db.execute(stmt)
#     post = result.scalar_one_or_none()
#
#     check_post_exist(post)
#
#     stmt = (
#         delete(DbPost)
#         .where(DbPost.id == post_id, DbPost.user_id == user.id)
#     )
#     await db.execute(stmt)
#     await db.commit()


# @app.post('/', response_model=UserOut, status_code=status.HTTP_201_CREATED)
# async def create_user(db: GetDb, payload: UserCreate = Body()):
#     try:
#         payload.password = get_password_hash(payload.password)
#         new_user = DbUser(**payload.dict())
#         db.add(new_user)
#         await db.commit()
#         await db.refresh(new_user)
#     except DBAPIError:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='email already exist')
#
#     return new_user
#
#
# @app.get('/', response_model=UserOut)
# async def get_current_user(user: UserLogin, db: GetDb):
#     user_stmt = select(DbUser).where(DbUser.id == user.id)
#     result = await db.execute(user_stmt)
#     current_user = result.scalar_one()
#
#     return current_user
#
#
# @app.put('/', response_model=UserOut, status_code=status.HTTP_202_ACCEPTED)
# async def update_current_user(user: UserLogin, db: GetDb, payload: UserCreate = Body()):
#     try:
#         payload.password = get_password_hash(payload.password)
#         update_stmt = (
#             update(DbUser)
#             .where(DbUser.id == user.id)
#             .values(**payload.dict())
#         )
#         await db.execute(update_stmt)
#         await db.commit()
#     except DBAPIError:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='email already exist')
#
#     updated_user_stmt = select(DbUser).where(DbUser.id == user.id)
#     result = await db.execute(updated_user_stmt)
#     updated_user = result.scalar_one()
#
#     return updated_user


@app.post('/{post_id}', status_code=status.HTTP_201_CREATED)
async def like_post(
        user: UserLogin, db: GetDb,
        post_id: int = Path(),
        like: bool = Query()
):
    # check post exist
    post_stmt = select(DbPost).where(DbPost.id == post_id)
    result = await db.execute(post_stmt)
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {post_id} does not exist')
    if like:
        try:
            like_stmt = insert(DbPostLike).values(post_id=post_id, user_id=user.id)
            await db.execute(like_stmt)
            await db.commit()
            return {'message': f'successfully like post {post_id}'}
        except DBAPIError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'already like post {post_id}')
    # if not like
    unlike_stmt = (
        delete(DbPostLike)
        .where(DbPostLike.post_id == post_id, DbPostLike.user_id == user.id)
    )
    await db.execute(unlike_stmt)
    await db.commit()
    return {'message': f'successfully unlike post {post_id}'}


if __name__ == '__main__':
    uvicorn.run('test:app', reload=True)

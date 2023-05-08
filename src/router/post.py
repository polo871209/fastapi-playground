from typing import Optional

from fastapi import APIRouter, Body, status, HTTPException, Path
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm.query import Query

from ..db import GetDb
from ..models import DbPost
from ..oauth2 import UserLogin
from ..schemas import PostCreate

router = APIRouter(
    prefix='/post',
    tags=['Post']
)


def check_post_exist(post):
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_post(
        db: GetDb, user: UserLogin,
        payload: PostCreate = Body()
):
    new_post_data = payload.dict()
    new_post_data["user_id"] = user.id

    # Insert the new post
    stmt = insert(DbPost).values(**new_post_data)
    await db.execute(stmt)
    await db.commit()

    # Fetch the newly inserted post
    stmt = select(DbPost).where(DbPost.user_id == user.id).order_by(DbPost.created_at.desc()).limit(1)
    result = await db.execute(stmt)
    new_post = result.scalar_one()

    return new_post


@router.get('/all')
async def get_all_posts(
        db: GetDb, user: UserLogin,
        limit: Optional[int] = Query(default=10, description='maximum amount of posts'),
        search: Optional[str] = Query(default='', description='search in title')
):
    """get all posts"""
    stmt = select(DbPost).where(DbPost.title.contains(search)).limit(limit)
    result = await db.execute(stmt)
    posts = result.scalars().all()
    return posts


@router.get('/{post_id}')
async def get_post(
        db: GetDb, user: UserLogin,
        post_id: int = Path()
):
    """get post by id"""
    stmt = select(DbPost).where(DbPost.id == post_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    await check_post_exist(post)

    return post


@router.put('/{post_id}', status_code=status.HTTP_202_ACCEPTED)
async def update_post(
        db: GetDb, user: UserLogin,
        post_id: int = Path(),
        payload: PostCreate = Body()):
    stmt = (
        update(DbPost)
        .where(DbPost.id == post_id, DbPost.user_id == user.id)
        .values(**payload.dict())
    )
    await db.execute(stmt)
    await db.commit()

    stmt = select(DbPost).where(DbPost.id == post_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    check_post_exist(post)

    return post


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        db: GetDb, user: UserLogin,
        post_id: int = Path()) -> None:
    """delete post by id"""
    # Check if post exists and if the user owns the post
    stmt = select(DbPost).where(DbPost.id == post_id, DbPost.user_id == user.id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    check_post_exist(post)

    stmt = (
        delete(DbPost)
        .where(DbPost.id == post_id, DbPost.user_id == user.id)
    )
    await db.execute(stmt)
    await db.commit()

from typing import Optional

from fastapi import APIRouter, Body, status, HTTPException, Path
from sqlalchemy import select, insert, update
from sqlalchemy.orm.query import Query

from src.db import GetDb
from src.models import DbPost
from ..schemas import PostCreate

router = APIRouter(
    prefix='/post',
    tags=['Post']
)


async def check_post_exist(post):
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")


# async def check_user_own_post(user, post):
#     if post != user:
#         raise HTTPException(status_code=403, detail="User does not own this post")


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_post(db: GetDb, payload: PostCreate = Body()):
    new_post_data = payload.dict()
    new_post_data["user_id"] = 1

    stmt = insert(DbPost).values(**new_post_data).returning(DbPost)
    result = await db.execute(stmt)

    new_post = result.fetchone()

    return new_post


@router.get('/all')
async def get_all_posts(db: GetDb,
                        limit: Optional[int] = Query(default=10, description='maximum amount of posts'),
                        search: Optional[str] = Query(default='', description='search in title')):
    """get all posts"""
    stmt = select(DbPost).where(DbPost.title.contains(search)).limit(limit)
    result = await db.execute(stmt)
    posts = result.scalars().all()
    return posts


@router.get('/{post_id}')
async def get_post(db: GetDb, post_id: int = Path()):
    """get post by id"""
    stmt = select(DbPost).where(DbPost.id == post_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    await check_post_exist(post)

    return post


@router.put('/{post_id}', status_code=status.HTTP_202_ACCEPTED)
async def update_post(db: GetDb, post_id: int = Path(), payload: PostCreate = Body()):
    """update post by id"""
    stmt = select(DbPost).where(DbPost.id == post_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    await check_post_exist(post)  # Assuming check_user_own_post() is an existing async function
    # await check_user_own_post(user, post)

    update_stmt = (
        update(DbPost)
        .where(DbPost.id == post_id)
        .values(**payload.dict())
    )
    await db.execute(update_stmt)
    await db.commit()

    return post


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(db: GetDb, post_id: int = Path()) -> None:
    """delete post by id"""
    stmt = (
        DbPost.__table__.delete()
        .where(DbPost.id == post_id)
    )
    await db.execute(stmt)
    await db.commit()

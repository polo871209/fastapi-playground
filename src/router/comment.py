from typing import List

from fastapi import APIRouter, Body, status, HTTPException, Path, Query as Parameters
from sqlalchemy import select, delete, update, insert
from sqlalchemy.exc import DBAPIError

from src.db import GetDb
from src.models import DbComment
from ..oauth2 import UserLogin
from ..schemas import CommentOut, CommentCreate

router = APIRouter(
    prefix='/comment',
    tags=['Comment']
)


def check_comment_exist(comment):
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='comment not found')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_comment(
        user: UserLogin, db: GetDb,
        post_id: int = Parameters(),
        payload: CommentCreate = Body()
):
    try:
        new_comment_data = payload.dict()
        new_comment_data["user_id"] = user.id
        new_comment_data["post_id"] = post_id

        comment_stmt = insert(DbComment).values(**new_comment_data)
        await db.execute(comment_stmt)
        await db.commit()
    except DBAPIError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post {post_id} not exist')

    return {**new_comment_data}


@router.get('/', response_model=List[CommentOut], status_code=status.HTTP_201_CREATED)
async def get_comment(
        user: UserLogin, db: GetDb,
        post_id: int = Parameters()
):
    """get your own comments"""
    comment_stmt = select(DbComment).where(DbComment.post_id == post_id, DbComment.user_id == user.id)
    result = await db.execute(comment_stmt)
    comments = result.scalars().all()

    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id {user.id} does not comment on post with id {post_id}')
    return comments


@router.put('/{comment_id}', status_code=status.HTTP_201_CREATED)
async def update_comment(
        user: UserLogin, db: GetDb,
        comment_id: int = Path(),
        payload: CommentCreate = Body()
):
    check_stmt = (
        select(DbComment)
        .where(DbComment.id == comment_id, DbComment.user_id == user.id)
    )
    result = await db.execute(check_stmt)
    comment = result.scalar_one_or_none()
    check_comment_exist(comment)

    update_stmt = (
        update(DbComment)
        .where(DbComment.id == comment_id, DbComment.user_id == user.id)
        .values(**payload.dict())
    )
    await db.execute(update_stmt)
    await db.commit()

    return {**payload.dict()}


@router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        user: UserLogin, db: GetDb,
        comment_id: int = Path()
) -> None:
    check_stmt = (
        select(DbComment)
        .where(DbComment.id == comment_id, DbComment.user_id == user.id)
    )
    result = await db.execute(check_stmt)
    comment = result.scalar_one_or_none()
    check_comment_exist(comment)

    delete_stmt = (
        delete(DbComment)
        .where(DbComment.id == comment_id, DbComment.user_id == user.id)
    )
    await db.execute(delete_stmt)
    await db.commit()

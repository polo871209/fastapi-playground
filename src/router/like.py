from fastapi import APIRouter, status, HTTPException, Path, Query
from sqlalchemy import select, delete, insert
from sqlalchemy.exc import DBAPIError

from src.db import GetDb
from src.models import DbPostLike, DbPost
from ..oauth2 import UserLogin

router = APIRouter(
    prefix='/like',
    tags=['Like']
)


@router.post('/{post_id}', status_code=status.HTTP_201_CREATED)
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

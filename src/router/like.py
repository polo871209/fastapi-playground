from fastapi import APIRouter, Body, status, HTTPException
from sqlalchemy.exc import DBAPIError

from src.db import GetDb
from src.models import DbPostLike, DbPost
from ..oauth2 import UserLogin
from ..schemas import Like

router = APIRouter(
    prefix='/like',
    tags=['Like']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
def like_post(user: UserLogin, db: GetDb, payload: Like = Body()):
    if not db.query(DbPost).where(DbPost.id == payload.post_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {payload.post_id} does not exist')
    if payload.dir == 1:
        try:
            db.add(DbPostLike(post_id=payload.post_id, user_id=user.id))
            db.commit()
            return {'message': 'successfully like post'}
        except DBAPIError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'already like post {payload.post_id}')

    db.query(DbPostLike).where(DbPostLike.post_id == payload.post_id, DbPostLike.user_id == user.id) \
        .delete(synchronize_session=False)
    db.commit()
    return {'message': 'successfully unlike post'}

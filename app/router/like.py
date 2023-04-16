from fastapi import APIRouter, Body, status, HTTPException
from sqlalchemy.exc import DBAPIError

from app import schemas
from app.database import models
from app.database.database import GetDb
from app.oauth2 import UserLogin

router = APIRouter(
    prefix='/like',
    tags=['Like']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
def like_post(user: UserLogin, db: GetDb, payload: schemas.Like = Body()):
    if not db.query(models.Post).where(models.Post.id == payload.post_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {payload.post_id} does not exist')
    if payload.dir == 1:
        try:
            db.add(models.PostLike(post_id=payload.post_id, user_id=user.id))
            db.commit()
            return {'message': 'successfully like post'}
        except DBAPIError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'already like post {payload.post_id}')

    db.query(models.PostLike).where(models.PostLike.post_id == payload.post_id, models.PostLike.user_id == user.id) \
        .delete(synchronize_session=False)
    db.commit()
    return {'message': 'successfully unlike post'}

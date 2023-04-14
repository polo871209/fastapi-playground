from typing import Type, List, Optional

from fastapi import APIRouter, Body, status, HTTPException
from sqlalchemy.orm.query import Query

from app import schemas
from app.database import models
from app.database.database import GetDb
from app.oauth2 import UserLogin

router = APIRouter(
    prefix='/post',
    tags=['Post']
)


def check_post_exist(query: Query, post_id: int) -> None:
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {post_id} does not exist')


def check_user_own_post(user: Type[models.User], post: Query[Type[models.Post]]) -> None:
    if user.id != post.first().user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='not authorize to perform requested action')


@router.post('/', response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
def create_post(user: UserLogin, db: GetDb, payload: schemas.Post = Body()):
    new_post = models.Post(user_id=user.id, **payload.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get('/', response_model=List[schemas.PostOut])
def get_posts(user: UserLogin, db: GetDb, limit: Optional[int] = 10, search: Optional[str] = ''):
    """
    get all posts
    - **limit**: maximum amount of posts
    - **search**: search in title
    """
    return db.query(models.Post).where(models.Post.title.contains(search)).limit(limit).all()


@router.get('/{post_id}', response_model=schemas.PostOut)
def get_post(user: UserLogin, db: GetDb, post_id: int):
    """get post by id"""
    post = db.query(models.Post).where(models.Post.id == post_id)
    check_post_exist(post, post_id)

    return post.first()


@router.put('/{post_id}', response_model=schemas.PostOut, status_code=status.HTTP_202_ACCEPTED)
def update_post(user: UserLogin, db: GetDb, post_id: int, payload: schemas.Post = Body()):
    """update post by id"""
    post = db.query(models.Post).where(models.Post.id == post_id)
    check_post_exist(post, post_id)
    check_user_own_post(user, post)
    post.update(payload.dict(), synchronize_session=False)
    db.commit()

    return post.first()


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(user: UserLogin, db: GetDb, post_id: int, ) -> None:
    """delete post by id"""
    post = db.query(models.Post).where(models.Post.id == post_id)
    check_post_exist(post, post_id)
    check_user_own_post(user, post)
    post.delete(synchronize_session=False)
    db.commit()

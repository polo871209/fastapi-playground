from typing import Type, Optional, List

from fastapi import APIRouter, Body, status, HTTPException, Path, Query as Parameters
from sqlalchemy.orm.query import Query

from src.db import GetDb
from src.models import DbPost, DbUser
from ..oauth2 import UserLogin
from ..schemas import PostCreate, PostOut

router = APIRouter(
    prefix='/post',
    tags=['Post']
)


def check_post_exist(query: Query, post_id: int) -> None:
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {post_id} does not exist')


def check_user_own_post(user: Type[DbUser], post: Query[Type[DbPost]]) -> None:
    if user.id != post.first().user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='not authorize to perform requested action')


@router.post('/', response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(user: UserLogin, db: GetDb, payload: PostCreate = Body()):
    new_post = DbPost(user_id=user.id, **payload.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get('/all', response_model=List[PostOut])
def get_all_posts(user: UserLogin, db: GetDb,
                  limit: Optional[int] = Parameters(default=10, description='maximum amount of posts'),
                  search: Optional[str] = Parameters(default='', description='search in title')):
    """get all posts"""
    return db.query(DbPost).where(DbPost.title.contains(search)).limit(limit).all()


@router.get('/{post_id}', response_model=PostOut)
def get_post(user: UserLogin, db: GetDb, post_id: int = Path()):
    """get post by id"""
    post = db.query(DbPost).where(DbPost.id == post_id)
    check_post_exist(post, post_id)
    return post.first()


@router.put('/{post_id}', response_model=PostOut, status_code=status.HTTP_202_ACCEPTED)
def update_post(user: UserLogin, db: GetDb, post_id: int = Path(), payload: PostCreate = Body()):
    """update post by id"""
    post = db.query(DbPost).where(DbPost.id == post_id)
    check_post_exist(post, post_id)
    check_user_own_post(user, post)
    post.update(payload.dict(), synchronize_session=False)
    db.commit()

    return post.first()


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(user: UserLogin, db: GetDb, post_id: int = Path()) -> None:
    """delete post by id"""
    post = db.query(DbPost).where(DbPost.id == post_id)
    check_post_exist(post, post_id)
    check_user_own_post(user, post)
    post.delete(synchronize_session=False)
    db.commit()

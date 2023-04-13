from typing import Type, List

from fastapi import APIRouter, Body, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

import app.oauth2 as oauth2
import app.schemas as schema
from app.database import model
from app.database.database import get_db

router = APIRouter(
    prefix='/post',
    tags=['post']
)


def check_post_exist(query: Query, post_id: int) -> None:
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {post_id} does not exist')


@router.post('/', response_model=schema.PostOut, status_code=status.HTTP_201_CREATED)
def create_post(payload: schema.Post = Body(), db: Session = Depends(get_db),
                user: Type[model.User] = Depends(oauth2.get_user)):
    new_post = model.Post(**payload.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get('/', response_model=List[schema.PostOut])
def get_posts(db: Session = Depends(get_db)):
    """get all posts"""
    return db.query(model.Post).all()


@router.get('/{post_id}', response_model=schema.PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """get post by id"""
    post = db.query(model.Post).where(model.Post.id == post_id)
    check_post_exist(post, post_id)

    return post.first()


@router.put('/{post_id}', response_model=schema.PostOut, status_code=status.HTTP_202_ACCEPTED)
def update_post(post_id: int, payload: schema.Post = Body(), db: Session = Depends(get_db),
                user: Type[model.User] = Depends(oauth2.get_user)):
    """update post by id"""
    post = db.query(model.Post).where(model.Post.id == post_id)
    check_post_exist(post, post_id)
    post.update(payload.dict(), synchronize_session=False)
    db.commit()

    return post.first()


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db),
                user: Type[model.User] = Depends(oauth2.get_user)) -> None:
    """delete post by id"""
    post = db.query(model.Post).where(model.Post.id == post_id)
    check_post_exist(post, post_id)
    post.delete(synchronize_session=False)
    db.commit()

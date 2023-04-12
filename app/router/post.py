from typing import Type

from fastapi import APIRouter, Body, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

import app.schema as schema
from app.database import model
from app.database.database import get_db

router = APIRouter(
    prefix='/post',
    tags=['post']
)


def check_post_exist(query: Query, post_id: int) -> None:
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {post_id} does not exist')


@router.get('/')
def get_posts(db: Session = Depends(get_db)):
    """
    get all posts
    """
    return db.query(model.Post).all()


@router.get('/{post_id}')
def get_post(post_id: int, db: Session = Depends(get_db)) -> Type[schema.Post]:
    """
    get post by id
    """
    post = db.query(model.Post).where(model.Post.id == post_id)
    check_post_exist(post, post_id)

    return post.first()


@router.post('/', response_model=schema.PostOut, status_code=status.HTTP_201_CREATED)
def create_post(payload: schema.Post = Body(), db: Session = Depends(get_db)) -> schema.Post:
    new_post = model.Post(**payload.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)) -> None:
    """
    delete post by id
    """
    post = db.query(model.Post).where(model.Post.id == post_id)
    check_post_exist(post, post_id)
    post.delete(synchronize_session=False)
    db.commit()


@router.put('/{post_id}')
def update_post(post_id: int, payload: schema.Post = Body(), db: Session = Depends(get_db)) -> Type[schema.Post]:
    """
    update post by id
    """
    post = db.query(model.Post).where(model.Post.id == post_id)
    check_post_exist(post, post_id)
    post.update(payload.dict(), synchronize_session=False)
    db.commit()

    return post.first()

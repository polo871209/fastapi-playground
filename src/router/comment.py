from typing import Type, List

from fastapi import APIRouter, Body, status, HTTPException, Path
from fastapi import Query as Parameters
from sqlalchemy.orm.query import Query

from src.database.database import GetDb
from src.database.models import DbPost, DbComment, DbUser
from src.oauth2 import UserLogin
from src.router.post import check_post_exist
from src.schemas import CommentOut, CommentCreate

router = APIRouter(
    prefix='/comment',
    tags=['Comment']
)


def check_comment_exist(query: Query, comment_id: int) -> None:
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'comment with id {comment_id} does not exist')


def check_user_own_comment(user: Type[DbUser], comment: Query[Type[DbComment]]) -> None:
    if user.id != comment.first().user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='not authorize to perform requested action')


@router.post('/', response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(user: UserLogin, db: GetDb, post_id: int = Parameters(), payload: CommentCreate = Body()):
    post = db.query(DbPost).where(DbPost.id == post_id)
    check_post_exist(post, post_id)
    new_comment = DbComment(user_id=user.id, post_id=post_id, **payload.dict())
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


@router.get('/', response_model=List[CommentOut], status_code=status.HTTP_201_CREATED)
def get_comment(user: UserLogin, db: GetDb, post_id: int = Parameters()):
    """get your own comments"""
    comments = db.query(DbComment) \
        .where(DbComment.post_id == post_id, DbComment.user_id == user.id).all()
    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id {user.id} does not comment on post with id {post_id}')
    return comments


@router.put('/{comment_id}', response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def update_comment(user: UserLogin, db: GetDb, comment_id: int = Path(), payload: CommentCreate = Body()):
    comment = db.query(DbComment).where(DbComment.id == comment_id)
    check_comment_exist(comment, comment_id)
    check_user_own_comment(user, comment)
    comment.update(payload.dict(), synchronize_session=False)
    db.commit()

    return comment.first()


@router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(user: UserLogin, db: GetDb, comment_id: int = Path()) -> None:
    comment = db.query(DbComment).where(DbComment.id == comment_id)
    check_comment_exist(comment, comment_id)
    check_user_own_comment(user, comment)
    comment.delete(synchronize_session=False)
    db.commit()
